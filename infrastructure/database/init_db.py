from infrastructure.database.models import Base
from infrastructure.database.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
