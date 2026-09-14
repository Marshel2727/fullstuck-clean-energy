"""SQLAlchemy models for cache data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Column, String,
)

from app.model.base import Base


class CacheEpoch(Base):
    __tablename__ = "cache_epochs"
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    namespace = Column(String(100), primary_key=True)
    revision = Column(String(32), nullable=False)
