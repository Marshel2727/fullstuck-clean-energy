"""SQLAlchemy models for audit data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Column, ForeignKey, Index, JSON, String, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_1", "entity_type", "entity_id", "created_at"),
        Index("ix_audit_logs_2", "actor_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    actor_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_audit_logs_actor_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(BIGINT(unsigned=True), nullable=False)
    changes_json = Column(JSON, nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
