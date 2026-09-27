"""Opt-in local profiling; SQL counts include authorization and cache-epoch reads."""
from contextvars import ContextVar
from sqlalchemy import event
from app.utils.database import engine

request_metrics = ContextVar("request_metrics", default=None)


@event.listens_for(engine, "before_cursor_execute")
def count_statement(conn, cursor, statement, parameters, context, executemany):
    stats = request_metrics.get()
    if stats is not None:
        stats["sql"] += 1
