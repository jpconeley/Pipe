from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from pvf.api.deps import SessionDep
from pvf.api.schemas import AskCreate, AskOut
from pvf.models import Ask, ListingStatus

router = APIRouter(prefix="/asks", tags=["asks"])


@router.get("", response_model=list[AskOut])
def list_asks(db: SessionDep, status: ListingStatus | None = None):
    stmt = select(Ask).order_by(Ask.created_at.desc())
    if status is not None:
        stmt = stmt.where(Ask.status == status)
    return db.execute(stmt).scalars().all()


@router.get("/{ask_id}", response_model=AskOut)
def get_ask(ask_id: int, db: SessionDep):
    ask = db.get(Ask, ask_id)
    if ask is None:
        raise HTTPException(404, "Ask not found")
    return ask


@router.post("", response_model=AskOut, status_code=201)
def create_ask(payload: AskCreate, db: SessionDep):
    ask = Ask(**payload.model_dump())
    db.add(ask)
    db.commit()
    db.refresh(ask)
    return ask
