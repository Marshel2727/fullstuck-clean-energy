"""SQLAlchemy models for device data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Enum, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        CheckConstraint("expected_interval_seconds > 0", name="ck_devices_1"),
        Index("ix_devices_1", "status", "last_seen_at"),
        Index("ix_devices_2", "system_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    device_code = Column(String(50), nullable=False, unique=True)
    system_id = Column(BIGINT(unsigned=True), ForeignKey("solar_systems.id", name="fk_devices_system_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    device_type = Column(Enum("inverter", "smart_meter", "solar_array", "battery"), nullable=False)
    serial_number = Column(String(191), nullable=False, unique=True)
    model = Column(String(255), nullable=False)
    firmware_version = Column(String(100), nullable=True)
    status = Column(Enum("normal", "warning", "offline", "unconnected"), nullable=False, server_default="unconnected")
    last_seen_at = Column(DATETIME(fsp=6), nullable=True)
    expected_interval_seconds = Column(Integer, nullable=False, server_default=text("60"))
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class DeviceTelemetry(Base):
    __tablename__ = "device_telemetry"
    __table_args__ = (
        UniqueConstraint("device_id", "recorded_at", name="uq_device_telemetry_1"),
        CheckConstraint("daily_yield_kwh IS NULL OR daily_yield_kwh >= 0", name="ck_device_telemetry_1"),
        CheckConstraint("total_yield_kwh IS NULL OR total_yield_kwh >= 0", name="ck_device_telemetry_2"),
        CheckConstraint("efficiency_percent IS NULL OR (efficiency_percent >= 0 AND efficiency_percent <= 100)", name="ck_device_telemetry_3"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    device_id = Column(BIGINT(unsigned=True), ForeignKey("devices.id", name="fk_device_telemetry_device_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    recorded_at = Column(DATETIME(fsp=6), nullable=False)
    received_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    current_power_kw = Column(Numeric(18, 6), nullable=True)
    voltage_v = Column(Numeric(18, 6), nullable=True)
    current_a = Column(Numeric(18, 6), nullable=True)
    grid_frequency_hz = Column(Numeric(18, 6), nullable=True)
    temperature_c = Column(Numeric(18, 6), nullable=True)
    daily_yield_kwh = Column(Numeric(18, 6), nullable=True)
    total_yield_kwh = Column(Numeric(18, 6), nullable=True)
    efficiency_percent = Column(Numeric(18, 6), nullable=True)
    quality_status = Column(Enum("valid", "estimated", "invalid"), nullable=False, server_default="valid")


class DeviceAlert(Base):
    __tablename__ = "device_alerts"
    __table_args__ = (
        CheckConstraint("resolved_at IS NULL OR resolved_at >= occurred_at", name="ck_device_alerts_1"),
        Index("ix_device_alerts_1", "device_id", "occurred_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    device_id = Column(BIGINT(unsigned=True), ForeignKey("devices.id", name="fk_device_alerts_device_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    code = Column(String(100), nullable=False)
    level = Column(Enum("info", "warning", "error"), nullable=False)
    message = Column(Text, nullable=False)
    occurred_at = Column(DATETIME(fsp=6), nullable=False)
    resolved_at = Column(DATETIME(fsp=6), nullable=True)


class DeviceRefreshJob(Base):
    __tablename__ = "device_refresh_jobs"
    __table_args__ = (
        Index("ix_device_refresh_jobs_1", "status", "requested_at"),
        Index("ix_device_refresh_jobs_2", "device_id"),
        Index("ix_device_refresh_jobs_3", "requested_by_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    device_id = Column(BIGINT(unsigned=True), ForeignKey("devices.id", name="fk_device_refresh_jobs_device_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    requested_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_device_refresh_jobs_requested_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    status = Column(Enum("pending", "running", "succeeded", "failed", "timed_out"), nullable=False, server_default="pending")
    requested_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    completed_at = Column(DATETIME(fsp=6), nullable=True)
    error_message = Column(Text, nullable=True)
