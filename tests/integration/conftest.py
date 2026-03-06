import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from infrastructure.database.models import Base


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:",echo=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)
