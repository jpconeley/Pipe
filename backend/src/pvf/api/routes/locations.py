from fastapi import APIRouter
from sqlalchemy import select

from pvf.api.deps import SessionDep
from pvf.api.schemas import LocationOut
from pvf.models import Location

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationOut])
def list_locations(db: SessionDep):
    return db.execute(select(Location).order_by(Location.name)).scalars().all()
