from sqlalchemy import Engine
from infrastructure.database.models import Base
from infrastructure.database.session import get_engine


def init_db(engine: Engine | None = None) -> None:
    Base.metadata.create_all(bind=engine or get_engine())


if __name__ == "__main__":
    init_db()
