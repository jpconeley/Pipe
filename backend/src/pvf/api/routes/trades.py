from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from pvf.api.deps import SessionDep
from pvf.api.schemas import TradeExecuteIn, TradeOut
from pvf.config import get_settings
from pvf.matching import grade_match
from pvf.models import Ask, Bid, ListingStatus, Trade
from pvf.pricing import estimate_freight

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/price-history", response_model=list[TradeOut])
def price_history(
    db: SessionDep,
    product_type: str,
    nominal_size_in: float,
    schedule_class: str,
    grade: str | None = None,
    days: int = 365,
):
    since = datetime.now(UTC) - timedelta(days=days)
    stmt = (
        select(Trade)
        .where(
            Trade.product_type == product_type,
            Trade.nominal_size_in == nominal_size_in,
            Trade.schedule_class == schedule_class,
            Trade.traded_at >= since,
        )
        .order_by(Trade.traded_at)
    )
    if grade:
        stmt = stmt.where(Trade.grade == grade)
    return db.execute(stmt).scalars().all()


@router.get("", response_model=list[TradeOut])
def list_trades(db: SessionDep, limit: int = 50):
    stmt = select(Trade).order_by(Trade.traded_at.desc()).limit(limit)
    return db.execute(stmt).scalars().all()


@router.post("/execute", response_model=TradeOut, status_code=201)
def execute_trade(payload: TradeExecuteIn, db: SessionDep):
    ask = db.get(Ask, payload.ask_id)
    bid = db.get(Bid, payload.bid_id)
    if ask is None or bid is None:
        raise HTTPException(404, "Ask or bid not found")
    if ask.status not in (ListingStatus.open, ListingStatus.partially_filled):
        raise HTTPException(400, "Ask is not open")
    if bid.status not in (ListingStatus.open, ListingStatus.partially_filled):
        raise HTTPException(400, "Bid is not open")
    same_spec = (
        ask.product_type == bid.product_type
        and ask.nominal_size_in == bid.nominal_size_in
        and ask.schedule_class == bid.schedule_class
    )
    if not same_spec:
        raise HTTPException(400, "Ask and bid specs don't match on size/schedule/product type")

    gm = grade_match(db, bid.grade, ask.grade)
    if gm is None:
        raise HTTPException(400, f"Ask grade {ask.grade} does not satisfy bid grade {bid.grade}")

    quantity = payload.quantity or min(ask.quantity_available, bid.quantity_remaining)
    if quantity <= 0 or quantity > ask.quantity_available or quantity > bid.quantity_remaining:
        raise HTTPException(400, "Requested quantity exceeds what's available on the ask or bid")

    settings = get_settings()
    fob = float(ask.price_per_unit) * (1 - gm.discount_pct)
    freight = estimate_freight(
        origin_lat=float(ask.location.lat),
        origin_lon=float(ask.location.lon),
        dest_lat=float(bid.destination.lat),
        dest_lon=float(bid.destination.lon),
        nominal_size_in=float(ask.nominal_size_in),
        schedule_class=ask.schedule_class,
        quantity_ft=quantity,
        settings=settings,
    )
    freight_per_unit = freight.freight_per_unit if freight else 0.0
    delivered = fob + freight_per_unit

    if bid.max_delivered_price_per_unit is not None and delivered > float(bid.max_delivered_price_per_unit):
        raise HTTPException(400, "Delivered price exceeds the bid's max price")

    trade = Trade(
        ask_id=ask.id,
        bid_id=bid.id,
        product_type=ask.product_type,
        nominal_size_in=ask.nominal_size_in,
        schedule_class=ask.schedule_class,
        grade=ask.grade,
        substitution_type=gm.substitution_type,
        quantity=quantity,
        unit=ask.unit,
        price_per_unit_fob=fob,
        freight_per_unit=freight_per_unit,
        delivered_price_per_unit=delivered,
        origin_location_id=ask.location_id,
        destination_location_id=bid.destination_location_id,
    )
    db.add(trade)

    ask.quantity_filled = float(ask.quantity_filled) + quantity
    ask.status = ListingStatus.filled if ask.quantity_available <= 0 else ListingStatus.partially_filled
    bid.quantity_filled = float(bid.quantity_filled) + quantity
    bid.status = ListingStatus.filled if bid.quantity_remaining <= 0 else ListingStatus.partially_filled

    db.commit()
    db.refresh(trade)
    return trade
