from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from pvf.api.deps import SessionDep
from pvf.api.schemas import BidCreate, BidOut, MatchOut
from pvf.matching import find_matches
from pvf.models import Bid, ListingStatus

router = APIRouter(prefix="/bids", tags=["bids"])


@router.get("", response_model=list[BidOut])
def list_bids(db: SessionDep, status: ListingStatus | None = None):
    stmt = select(Bid).order_by(Bid.created_at.desc())
    if status is not None:
        stmt = stmt.where(Bid.status == status)
    return db.execute(stmt).scalars().all()


@router.get("/{bid_id}", response_model=BidOut)
def get_bid(bid_id: int, db: SessionDep):
    bid = db.get(Bid, bid_id)
    if bid is None:
        raise HTTPException(404, "Bid not found")
    return bid


@router.post("", response_model=BidOut, status_code=201)
def create_bid(payload: BidCreate, db: SessionDep):
    bid = Bid(**payload.model_dump())
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return bid


@router.get("/{bid_id}/matches", response_model=list[MatchOut])
def get_matches(bid_id: int, db: SessionDep):
    bid = db.get(Bid, bid_id)
    if bid is None:
        raise HTTPException(404, "Bid not found")
    candidates = find_matches(db, bid)
    return [
        MatchOut(
            ask=c.ask,
            matched_quantity=c.matched_quantity,
            substitution_type=c.substitution_type,
            discount_pct=c.discount_pct,
            substitution_note=c.substitution_note,
            distance_miles=c.distance_miles,
            freight_per_unit=c.freight_per_unit,
            price_per_unit_fob=c.price_per_unit_fob,
            delivered_price_per_unit=c.delivered_price_per_unit,
        )
        for c in candidates
    ]
