from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from pvf.db import get_session


def db_session() -> Iterator[Session]:
    yield from get_session()


SessionDep = Annotated[Session, Depends(db_session)]
