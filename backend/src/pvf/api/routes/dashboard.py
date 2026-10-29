from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import func, select

from pvf.api.deps import SessionDep
from pvf.api.schemas import DashboardOut
from pvf.models import Ask, Bid, ListingStatus, Trade

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(db: SessionDep):
    open_statuses = [ListingStatus.open, ListingStatus.partially_filled]
    open_asks = db.scalar(select(func.count()).select_from(Ask).where(Ask.status.in_(open_statuses)))
    open_bids = db.scalar(select(func.count()).select_from(Bid).where(Bid.status.in_(open_statuses)))
    since = datetime.now(UTC) - timedelta(days=30)
    trades_30d = db.scalar(select(func.count()).select_from(Trade).where(Trade.traded_at >= since))
    volume_30d = db.scalar(select(func.coalesce(func.sum(Trade.quantity), 0)).where(Trade.traded_at >= since))
    recent = db.execute(select(Trade).order_by(Trade.traded_at.desc()).limit(10)).scalars().all()

    return DashboardOut(
        open_asks=open_asks or 0,
        open_bids=open_bids or 0,
        trades_30d=trades_30d or 0,
        volume_30d_units=float(volume_30d or 0),
        recent_trades=recent,
    )
