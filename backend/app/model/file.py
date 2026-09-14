"""SQLAlchemy models for file data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Column, Enum, ForeignKey, Index, String, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class StoredFile(Base):
    __tablename__ = "files"
    __table_args__ = (
        Index("ix_files_1", "uploaded_by_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    uploaded_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_files_uploaded_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    storage_key = Column(String(512), nullable=False, unique=True)
    original_name = Column(String(255), nullable=False)
    mime_type = Column(String(127), nullable=False)
    size_bytes = Column(BIGINT(unsigned=True), nullable=False)
    visibility = Column(Enum("public", "private"), nullable=False, server_default="private")
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
