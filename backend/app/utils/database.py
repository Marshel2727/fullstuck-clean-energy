from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.utils.config import get_settings

engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"connect_timeout": 10},
)


@event.listens_for(engine, "connect")
def configure_connection(dbapi_connection, connection_record) -> None:
    with dbapi_connection.cursor() as cursor:
        cursor.execute("SET time_zone = '+00:00'")
        cursor.execute(
            "SET SESSION sql_mode = "
            "'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'"
        )


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    # A write service must explicitly commit; failed requests always roll back.
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
