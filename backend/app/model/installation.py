"""SQLAlchemy models for installation data; DATETIME values use naive UTC."""
from sqlalchemy import (
    CheckConstraint, Column, Computed, Enum, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class InstallationRequest(Base):
    __tablename__ = "installation_requests"
    __table_args__ = (
        CheckConstraint("pln_power_va > 0 AND monthly_bill_idr >= 0 AND roof_area_sqm > 0", name="ck_installation_requests_1"),
        CheckConstraint("version > 0", name="ck_installation_requests_2"),
        Index("ix_installation_requests_1", "status", "created_at"),
        Index("ix_installation_requests_2", "customer_id", "created_at"),
        Index("ix_installation_requests_3", "site_id"),
        Index("ix_installation_requests_4", "submitted_by_user_id"),
        Index("ix_installation_requests_5", "calculation_id"),
        Index("ix_installation_requests_6", "package_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ticket_number = Column(String(50), nullable=False, unique=True)
    customer_id = Column(BIGINT(unsigned=True), ForeignKey("customers.id", name="fk_installation_requests_customer_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    site_id = Column(BIGINT(unsigned=True), ForeignKey("sites.id", name="fk_installation_requests_site_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    submitted_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_installation_requests_submitted_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    calculation_id = Column(BIGINT(unsigned=True), ForeignKey("solar_calculations.id", name="fk_installation_requests_calculation_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    package_id = Column(BIGINT(unsigned=True), ForeignKey("solar_packages.id", name="fk_installation_requests_package_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(32), nullable=False)
    email = Column(String(254), nullable=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(12), nullable=True)
    property_type = Column(Enum("household", "business", "industry", "school", "other"), nullable=False)
    pln_power_va = Column(Integer, nullable=False)
    monthly_bill_idr = Column(Numeric(18, 2), nullable=False)
    roof_area_sqm = Column(Numeric(18, 6), nullable=False)
    package_snapshot_json = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(Enum("Diajukan", "Diverifikasi", "Menunggu Survei", "Penawaran", "Disetujui", "Dijadwalkan", "Instalasi", "Selesai", "Dibatalkan"), nullable=False, server_default="Diajukan")
    consent_version = Column(String(50), nullable=False)
    consented_at = Column(DATETIME(fsp=6), nullable=False)
    version = Column(Integer, nullable=False, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class RequestStatusLog(Base):
    __tablename__ = "request_status_logs"
    __table_args__ = (
        Index("ix_request_status_logs_1", "request_id", "created_at"),
        Index("ix_request_status_logs_2", "actor_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    request_id = Column(BIGINT(unsigned=True), ForeignKey("installation_requests.id", name="fk_request_status_logs_request_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    from_status = Column(Enum("Diajukan", "Diverifikasi", "Menunggu Survei", "Penawaran", "Disetujui", "Dijadwalkan", "Instalasi", "Selesai", "Dibatalkan"), nullable=True)
    to_status = Column(Enum("Diajukan", "Diverifikasi", "Menunggu Survei", "Penawaran", "Disetujui", "Dijadwalkan", "Instalasi", "Selesai", "Dibatalkan"), nullable=False)
    note = Column(Text, nullable=False)
    actor_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_request_status_logs_actor_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    actor_name_snapshot = Column(String(255), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))


class RequestAssignment(Base):
    __tablename__ = "request_assignments"
    __table_args__ = (
        CheckConstraint("ended_at IS NULL OR ended_at >= assigned_at", name="ck_request_assignments_1"),
        Index("ix_request_assignments_1", "request_id"),
        Index("ix_request_assignments_2", "technician_id"),
        Index("ix_request_assignments_3", "assigned_by_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    request_id = Column(BIGINT(unsigned=True), ForeignKey("installation_requests.id", name="fk_request_assignments_request_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    technician_id = Column(BIGINT(unsigned=True), ForeignKey("technicians.id", name="fk_request_assignments_technician_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    assignment_role = Column(Enum("lead", "member"), nullable=False, server_default="member")
    field_status = Column(Enum("assigned", "on_site", "completed"), nullable=False, server_default="assigned")
    assigned_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_request_assignments_assigned_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    assigned_at = Column(DATETIME(fsp=6), nullable=False)
    ended_at = Column(DATETIME(fsp=6), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class RequestAppointment(Base):
    __tablename__ = "request_appointments"
    __table_args__ = (
        CheckConstraint("scheduled_end_at IS NULL OR scheduled_end_at > scheduled_start_at", name="ck_request_appointments_1"),
        Index("ix_request_appointments_1", "request_id", "appointment_type", "status"),
        Index("ix_request_appointments_2", "created_by_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    request_id = Column(BIGINT(unsigned=True), ForeignKey("installation_requests.id", name="fk_request_appointments_request_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    appointment_type = Column(Enum("survey", "installation"), nullable=False)
    scheduled_start_at = Column(DATETIME(fsp=6), nullable=False)
    scheduled_end_at = Column(DATETIME(fsp=6), nullable=True)
    status = Column(Enum("scheduled", "completed", "cancelled"), nullable=False, server_default="scheduled")
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_request_appointments_created_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class Quotation(Base):
    __tablename__ = "quotations"
    __table_args__ = (
        UniqueConstraint("request_id", "revision_number", name="uq_quotations_1"),
        UniqueConstraint("accepted_request_id", name="uq_quotations_2"),
        CheckConstraint("revision_number > 0 AND amount_idr >= 0", name="ck_quotations_1"),
        Index("ix_quotations_1", "file_id"),
        Index("ix_quotations_2", "created_by_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    request_id = Column(BIGINT(unsigned=True), ForeignKey("installation_requests.id", name="fk_quotations_request_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    revision_number = Column(Integer, nullable=False)
    amount_idr = Column(Numeric(18, 2), nullable=False)
    status = Column(Enum("draft", "sent", "accepted", "rejected", "superseded"), nullable=False, server_default="draft")
    notes = Column(Text, nullable=True)
    issued_at = Column(DATETIME(fsp=6), nullable=True)
    accepted_at = Column(DATETIME(fsp=6), nullable=True)
    file_id = Column(BIGINT(unsigned=True), ForeignKey("files.id", name="fk_quotations_file_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    created_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_quotations_created_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    accepted_request_id = Column(BIGINT(unsigned=True), Computed("CASE WHEN status = 'accepted' THEN request_id ELSE NULL END", persisted=True), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class RequestDocument(Base):
    __tablename__ = "request_documents"
    __table_args__ = (
        Index("ix_request_documents_1", "request_id"),
        Index("ix_request_documents_2", "file_id"),
        Index("ix_request_documents_3", "reviewed_by_user_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    request_id = Column(BIGINT(unsigned=True), ForeignKey("installation_requests.id", name="fk_request_documents_request_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    document_type = Column(Enum("roof_photo", "electricity_bill", "slo", "pln_permit", "spk", "design", "other"), nullable=False)
    file_id = Column(BIGINT(unsigned=True), ForeignKey("files.id", name="fk_request_documents_file_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    document_number = Column(String(100), nullable=True)
    status = Column(Enum("pending", "in_progress", "approved", "rejected"), nullable=False, server_default="pending")
    notes = Column(Text, nullable=True)
    issued_at = Column(DATETIME(fsp=6), nullable=True)
    reviewed_by_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_request_documents_reviewed_by_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
