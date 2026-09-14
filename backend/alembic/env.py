from alembic import context
from sqlalchemy import create_engine, pool, text

from app.utils.config import get_settings
from app.model import Base  # importing the package registers all feature tables

config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        dialect_name="mysql", target_metadata=target_metadata,
        literal_binds=True, compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(get_settings().database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        connection.execute(text("SET time_zone = '+00:00'"))
        connection.commit()
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
