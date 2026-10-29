import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from pvf.db import Base

TEST_DATABASE_URL = "postgresql+psycopg://pvf:pvf@localhost:5432/pvf_test"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db(engine):
    """A session bound to a transaction that's rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
