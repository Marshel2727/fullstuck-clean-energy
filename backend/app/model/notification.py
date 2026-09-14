"""SQLAlchemy models for notification data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Enum, ForeignKey, Index, Integer, Numeric, String, Text, Time, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    __table_args__ = (
        CheckConstraint("power_drop_threshold_percent > 0 AND power_drop_threshold_percent <= 100", name="ck_notification_preferences_1"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_notification_preferences_user_id", ondelete="CASCADE", use_alter=True), primary_key=True)
    notify_power_drop = Column(Boolean, nullable=False, server_default=text("1"))
    notify_daily_report = Column(Boolean, nullable=False, server_default=text("1"))
    notify_maintenance = Column(Boolean, nullable=False, server_default=text("1"))
    power_drop_threshold_percent = Column(Numeric(5, 2), nullable=False, server_default=text("40"))
    daily_report_time = Column(Time, nullable=False, server_default=text("'18:00:00'"))
    timezone = Column(String(64), nullable=False, server_default="Asia/Jakarta")
    whatsapp_enabled = Column(Boolean, nullable=False, server_default=text("0"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    __table_args__ = (
        CheckConstraint("attempt_count >= 0", name="ck_notification_deliveries_1"),
        Index("ix_notification_deliveries_1", "status", "scheduled_at"),
        Index("ix_notification_deliveries_2", "user_id", "created_at"),
        Index("ix_notification_deliveries_3", "system_id"),
        Index("ix_notification_deliveries_4", "device_alert_id"),
        Index("ix_notification_deliveries_5", "maintenance_task_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_notification_deliveries_user_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    system_id = Column(BIGINT(unsigned=True), ForeignKey("solar_systems.id", name="fk_notification_deliveries_system_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    device_alert_id = Column(BIGINT(unsigned=True), ForeignKey("device_alerts.id", name="fk_notification_deliveries_device_alert_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    maintenance_task_id = Column(BIGINT(unsigned=True), ForeignKey("maintenance_tasks.id", name="fk_notification_deliveries_maintenance_task_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    event_type = Column(Enum("power_drop", "daily_report", "maintenance", "device_alert", "installation_update"), nullable=False)
    channel = Column(Enum("whatsapp", "email", "in_app"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    scheduled_at = Column(DATETIME(fsp=6), nullable=False)
    sent_at = Column(DATETIME(fsp=6), nullable=True)
    read_at = Column(DATETIME(fsp=6), nullable=True)
    status = Column(Enum("pending", "sending", "sent", "failed", "cancelled"), nullable=False, server_default="pending")
    attempt_count = Column(Integer, nullable=False, server_default=text("0"))
    provider_message_id = Column(String(255), nullable=True)
    deduplication_key = Column(String(191), nullable=False, unique=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
