"""SQLAlchemy models for maintenance data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, Column, Enum, ForeignKey, Index, String, Text, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class Technician(Base):
    __tablename__ = "technicians"
    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=True)
    qualification = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"
    __table_args__ = (
        Index("ix_maintenance_tasks_1", "status", "scheduled_at"),
        Index("ix_maintenance_tasks_2", "system_id"),
        Index("ix_maintenance_tasks_3", "technician_id"),
        Index("ix_maintenance_tasks_4", "created_by_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    system_id = Column(BIGINT(unsigned=True), ForeignKey("solar_systems.id", name="fk_maintenance_tasks_system_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    technician_id = Column(BIGINT(unsigned=True), ForeignKey("technicians.id", name="fk_maintenance_tasks_technician_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    task_type = Column(String(100), nullable=False)
    scheduled_at = Column(DATETIME(fsp=6), nullable=False)
    completed_at = Column(DATETIME(fsp=6), nullable=True)
    status = Column(Enum("scheduled", "in_progress", "completed", "cancelled"), nullable=False, server_default="scheduled")
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_maintenance_tasks_created_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
