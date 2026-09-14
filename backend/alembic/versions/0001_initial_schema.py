"""Initial SolarSync feature schema (33 tables).

Frozen DDL: this revision intentionally does not import application models.
"""
from alembic import op
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Computed, Date, Enum, ForeignKey,
    Index, Integer, JSON, Numeric, String, Text, Time, UniqueConstraint, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, LONGTEXT

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "files",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("uploaded_by_user_id", BIGINT(unsigned=True), nullable=True),
        Column("storage_key", String(512), nullable=False, unique=True),
        Column("original_name", String(255), nullable=False),
        Column("mime_type", String(127), nullable=False),
        Column("size_bytes", BIGINT(unsigned=True), nullable=False),
        Column("visibility", Enum("public", "private"), nullable=False, server_default="private"),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_files_1", "files", ["uploaded_by_user_id"])
    op.create_table(
        "users",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("name", String(255), nullable=False),
        Column("email", String(254), nullable=True),
        Column("phone", String(32), nullable=True),
        Column("password_hash", String(255), nullable=False),
        Column("role", Enum("customer", "admin"), nullable=False, server_default="customer"),
        Column("is_active", Boolean, nullable=False, server_default=text("1")),
        Column("avatar_file_id", BIGINT(unsigned=True), nullable=True),
        Column("email_verified_at", DATETIME(fsp=6), nullable=True),
        Column("phone_verified_at", DATETIME(fsp=6), nullable=True),
        Column("last_login_at", DATETIME(fsp=6), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        UniqueConstraint("email", name="uq_users_1"),
        UniqueConstraint("phone", name="uq_users_2"),
        CheckConstraint("email IS NOT NULL OR phone IS NOT NULL", name="ck_users_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_users_1", "users", ["avatar_file_id"])
    op.create_table(
        "customers",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("customer_code", String(40), nullable=False, unique=True),
        Column("user_id", BIGINT(unsigned=True), nullable=True, unique=True),
        Column("name", String(255), nullable=False),
        Column("email", String(254), nullable=True),
        Column("phone", String(32), nullable=False),
        Column("notes", Text, nullable=True),
        Column("is_active", Boolean, nullable=False, server_default=text("1")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_customers_1", "customers", ["name"])
    op.create_index("ix_customers_2", "customers", ["phone"])
    op.create_table(
        "auth_sessions",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("user_id", BIGINT(unsigned=True), nullable=False),
        Column("refresh_token_hash", String(64), nullable=False, unique=True),
        Column("expires_at", DATETIME(fsp=6), nullable=False),
        Column("revoked_at", DATETIME(fsp=6), nullable=True),
        Column("last_used_at", DATETIME(fsp=6), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_auth_sessions_1", "auth_sessions", ["user_id","expires_at"])
    op.create_table(
        "account_tokens",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("user_id", BIGINT(unsigned=True), nullable=False),
        Column("purpose", Enum("password_reset", "account_invitation"), nullable=False),
        Column("token_hash", String(64), nullable=False, unique=True),
        Column("expires_at", DATETIME(fsp=6), nullable=False),
        Column("used_at", DATETIME(fsp=6), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_account_tokens_1", "account_tokens", ["user_id","purpose"])
    op.create_table(
        "notification_preferences",
        Column("user_id", BIGINT(unsigned=True), primary_key=True),
        Column("notify_power_drop", Boolean, nullable=False, server_default=text("1")),
        Column("notify_daily_report", Boolean, nullable=False, server_default=text("1")),
        Column("notify_maintenance", Boolean, nullable=False, server_default=text("1")),
        Column("power_drop_threshold_percent", Numeric(5, 2), nullable=False, server_default=text("40")),
        Column("daily_report_time", Time, nullable=False, server_default=text("'18:00:00'")),
        Column("timezone", String(64), nullable=False, server_default="Asia/Jakarta"),
        Column("whatsapp_enabled", Boolean, nullable=False, server_default=text("0")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("power_drop_threshold_percent > 0 AND power_drop_threshold_percent <= 100", name="ck_notification_preferences_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "sites",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("customer_id", BIGINT(unsigned=True), nullable=False),
        Column("name", String(255), nullable=False),
        Column("address", Text, nullable=False),
        Column("city", String(100), nullable=False),
        Column("postal_code", String(12), nullable=True),
        Column("property_type", Enum("household", "business", "industry", "school", "other"), nullable=False),
        Column("pln_power_va", Integer, nullable=False),
        Column("roof_area_sqm", Numeric(18, 6), nullable=False),
        Column("roof_type", Enum("genteng", "dak_beton", "spandek_metal", "asbes", "other"), nullable=True),
        Column("roof_orientation", Enum("utara", "selatan", "timur", "barat", "optimal"), nullable=True),
        Column("shading_condition", Enum("none", "partial", "heavy"), nullable=True),
        Column("timezone", String(64), nullable=False, server_default="Asia/Jakarta"),
        Column("is_active", Boolean, nullable=False, server_default=text("1")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("pln_power_va > 0", name="ck_sites_1"),
        CheckConstraint("roof_area_sqm >= 0", name="ck_sites_2"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_sites_1", "sites", ["customer_id"])
    op.create_table(
        "solar_packages",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("slug", String(191), nullable=False, unique=True),
        Column("name", String(255), nullable=False),
        Column("segment", Enum("household", "business", "industry", "school", "other"), nullable=False),
        Column("capacity_kwp", Numeric(18, 6), nullable=False),
        Column("tagline", String(255), nullable=False),
        Column("description", Text, nullable=False),
        Column("price_from_idr", Numeric(18, 2), nullable=False),
        Column("estimated_monthly_production_kwh", Numeric(18, 6), nullable=False),
        Column("estimated_monthly_savings_idr", Numeric(18, 2), nullable=False),
        Column("warranty_panels_years", Integer, nullable=False),
        Column("warranty_inverter_years", Integer, nullable=False),
        Column("warranty_workmanship_years", Integer, nullable=False),
        Column("recommended_roof_area_sqm", Numeric(18, 6), nullable=False),
        Column("ideal_for", Text, nullable=False),
        Column("is_popular", Boolean, nullable=False, server_default=text("0")),
        Column("is_active", Boolean, nullable=False, server_default=text("1")),
        Column("sort_order", Integer, nullable=False, server_default=text("0")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("capacity_kwp > 0", name="ck_solar_packages_1"),
        CheckConstraint("price_from_idr >= 0", name="ck_solar_packages_2"),
        CheckConstraint("estimated_monthly_production_kwh >= 0", name="ck_solar_packages_3"),
        CheckConstraint("estimated_monthly_savings_idr >= 0", name="ck_solar_packages_4"),
        CheckConstraint("recommended_roof_area_sqm >= 0", name="ck_solar_packages_5"),
        CheckConstraint("warranty_panels_years >= 0 AND warranty_inverter_years >= 0 AND warranty_workmanship_years >= 0", name="ck_solar_packages_6"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "package_components",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("package_id", BIGINT(unsigned=True), nullable=False),
        Column("name", String(255), nullable=False),
        Column("specs", Text, nullable=False),
        Column("quantity", Integer, nullable=False),
        Column("sort_order", Integer, nullable=False, server_default=text("0")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("quantity > 0", name="ck_package_components_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_package_components_1", "package_components", ["package_id"])
    op.create_table(
        "package_items",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("package_id", BIGINT(unsigned=True), nullable=False),
        Column("item_type", Enum("feature", "included_service", "exclusion"), nullable=False),
        Column("content", Text, nullable=False),
        Column("sort_order", Integer, nullable=False, server_default=text("0")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_package_items_1", "package_items", ["package_id"])
    op.create_table(
        "calculation_profiles",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("version", String(50), nullable=False, unique=True),
        Column("sun_hours_per_day", Numeric(18, 6), nullable=False),
        Column("system_efficiency", Numeric(18, 6), nullable=False),
        Column("panel_watt_peak", Integer, nullable=False),
        Column("area_per_panel_sqm", Numeric(18, 6), nullable=False),
        Column("cost_per_kwp_min_idr", Numeric(18, 2), nullable=False),
        Column("cost_per_kwp_max_idr", Numeric(18, 2), nullable=False),
        Column("emission_factor", Numeric(18, 6), nullable=False),
        Column("tree_absorption_kg_per_year", Numeric(18, 6), nullable=False),
        Column("tariff_rules_json", JSON, nullable=False),
        Column("effective_from", DATETIME(fsp=6), nullable=False),
        Column("is_active", Boolean, nullable=False, server_default=text("1")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("sun_hours_per_day > 0 AND sun_hours_per_day <= 24", name="ck_calculation_profiles_1"),
        CheckConstraint("system_efficiency > 0 AND system_efficiency <= 1", name="ck_calculation_profiles_2"),
        CheckConstraint("panel_watt_peak > 0 AND area_per_panel_sqm > 0", name="ck_calculation_profiles_3"),
        CheckConstraint("cost_per_kwp_min_idr >= 0 AND cost_per_kwp_max_idr >= cost_per_kwp_min_idr", name="ck_calculation_profiles_4"),
        CheckConstraint("emission_factor >= 0 AND tree_absorption_kg_per_year > 0", name="ck_calculation_profiles_5"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "solar_calculations",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("user_id", BIGINT(unsigned=True), nullable=True),
        Column("profile_id", BIGINT(unsigned=True), nullable=False),
        Column("access_token_hash", String(64), nullable=True),
        Column("expires_at", DATETIME(fsp=6), nullable=True),
        Column("city", String(100), nullable=False),
        Column("property_type", Enum("household", "business", "industry", "school", "other"), nullable=False),
        Column("monthly_kwh", Numeric(18, 6), nullable=False),
        Column("monthly_bill_idr", Numeric(18, 2), nullable=False),
        Column("pln_power_va", Integer, nullable=False),
        Column("roof_area_sqm", Numeric(18, 6), nullable=False),
        Column("roof_orientation", Enum("utara", "selatan", "timur", "barat", "optimal"), nullable=True),
        Column("shading_condition", Enum("none", "partial", "heavy"), nullable=True),
        Column("target_coverage_percent", Numeric(5, 2), nullable=False),
        Column("result_json", JSON, nullable=False),
        Column("assumptions_json", JSON, nullable=False),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        UniqueConstraint("access_token_hash", name="uq_solar_calculations_1"),
        CheckConstraint("monthly_kwh >= 0 AND monthly_bill_idr >= 0", name="ck_solar_calculations_1"),
        CheckConstraint("pln_power_va > 0 AND roof_area_sqm > 0", name="ck_solar_calculations_2"),
        CheckConstraint("target_coverage_percent > 0 AND target_coverage_percent <= 100", name="ck_solar_calculations_3"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_solar_calculations_1", "solar_calculations", ["user_id","created_at"])
    op.create_index("ix_solar_calculations_2", "solar_calculations", ["profile_id"])
    op.create_table(
        "installation_requests",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("ticket_number", String(50), nullable=False, unique=True),
        Column("customer_id", BIGINT(unsigned=True), nullable=True),
        Column("site_id", BIGINT(unsigned=True), nullable=True),
        Column("submitted_by_user_id", BIGINT(unsigned=True), nullable=True),
        Column("calculation_id", BIGINT(unsigned=True), nullable=True),
        Column("package_id", BIGINT(unsigned=True), nullable=True),
        Column("full_name", String(255), nullable=False),
        Column("phone_number", String(32), nullable=False),
        Column("email", String(254), nullable=True),
        Column("address", Text, nullable=False),
        Column("city", String(100), nullable=False),
        Column("postal_code", String(12), nullable=True),
        Column("property_type", Enum("household", "business", "industry", "school", "other"), nullable=False),
        Column("pln_power_va", Integer, nullable=False),
        Column("monthly_bill_idr", Numeric(18, 2), nullable=False),
        Column("roof_area_sqm", Numeric(18, 6), nullable=False),
        Column("package_snapshot_json", JSON, nullable=True),
        Column("notes", Text, nullable=True),
        Column("status", Enum("Diajukan", "Diverifikasi", "Menunggu Survei", "Penawaran", "Disetujui", "Dijadwalkan", "Instalasi", "Selesai", "Dibatalkan"), nullable=False, server_default="Diajukan"),
        Column("consent_version", String(50), nullable=False),
        Column("consented_at", DATETIME(fsp=6), nullable=False),
        Column("version", Integer, nullable=False, server_default=text("1")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("pln_power_va > 0 AND monthly_bill_idr >= 0 AND roof_area_sqm > 0", name="ck_installation_requests_1"),
        CheckConstraint("version > 0", name="ck_installation_requests_2"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_installation_requests_1", "installation_requests", ["status","created_at"])
    op.create_index("ix_installation_requests_2", "installation_requests", ["customer_id","created_at"])
    op.create_index("ix_installation_requests_3", "installation_requests", ["site_id"])
    op.create_index("ix_installation_requests_4", "installation_requests", ["submitted_by_user_id"])
    op.create_index("ix_installation_requests_5", "installation_requests", ["calculation_id"])
    op.create_index("ix_installation_requests_6", "installation_requests", ["package_id"])
    op.create_table(
        "request_status_logs",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("request_id", BIGINT(unsigned=True), nullable=False),
        Column("from_status", Enum("Diajukan", "Diverifikasi", "Menunggu Survei", "Penawaran", "Disetujui", "Dijadwalkan", "Instalasi", "Selesai", "Dibatalkan"), nullable=True),
        Column("to_status", Enum("Diajukan", "Diverifikasi", "Menunggu Survei", "Penawaran", "Disetujui", "Dijadwalkan", "Instalasi", "Selesai", "Dibatalkan"), nullable=False),
        Column("note", Text, nullable=False),
        Column("actor_user_id", BIGINT(unsigned=True), nullable=True),
        Column("actor_name_snapshot", String(255), nullable=False),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_request_status_logs_1", "request_status_logs", ["request_id","created_at"])
    op.create_index("ix_request_status_logs_2", "request_status_logs", ["actor_user_id"])
    op.create_table(
        "technicians",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("name", String(255), nullable=False),
        Column("phone", String(32), nullable=True),
        Column("qualification", String(255), nullable=True),
        Column("is_active", Boolean, nullable=False, server_default=text("1")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "request_assignments",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("request_id", BIGINT(unsigned=True), nullable=False),
        Column("technician_id", BIGINT(unsigned=True), nullable=False),
        Column("assignment_role", Enum("lead", "member"), nullable=False, server_default="member"),
        Column("field_status", Enum("assigned", "on_site", "completed"), nullable=False, server_default="assigned"),
        Column("assigned_by_user_id", BIGINT(unsigned=True), nullable=False),
        Column("assigned_at", DATETIME(fsp=6), nullable=False),
        Column("ended_at", DATETIME(fsp=6), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("ended_at IS NULL OR ended_at >= assigned_at", name="ck_request_assignments_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_request_assignments_1", "request_assignments", ["request_id"])
    op.create_index("ix_request_assignments_2", "request_assignments", ["technician_id"])
    op.create_index("ix_request_assignments_3", "request_assignments", ["assigned_by_user_id"])
    op.create_table(
        "request_appointments",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("request_id", BIGINT(unsigned=True), nullable=False),
        Column("appointment_type", Enum("survey", "installation"), nullable=False),
        Column("scheduled_start_at", DATETIME(fsp=6), nullable=False),
        Column("scheduled_end_at", DATETIME(fsp=6), nullable=True),
        Column("status", Enum("scheduled", "completed", "cancelled"), nullable=False, server_default="scheduled"),
        Column("notes", Text, nullable=True),
        Column("created_by_user_id", BIGINT(unsigned=True), nullable=False),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("scheduled_end_at IS NULL OR scheduled_end_at > scheduled_start_at", name="ck_request_appointments_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_request_appointments_1", "request_appointments", ["request_id","appointment_type","status"])
    op.create_index("ix_request_appointments_2", "request_appointments", ["created_by_user_id"])
    op.create_table(
        "quotations",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("request_id", BIGINT(unsigned=True), nullable=False),
        Column("revision_number", Integer, nullable=False),
        Column("amount_idr", Numeric(18, 2), nullable=False),
        Column("status", Enum("draft", "sent", "accepted", "rejected", "superseded"), nullable=False, server_default="draft"),
        Column("notes", Text, nullable=True),
        Column("issued_at", DATETIME(fsp=6), nullable=True),
        Column("accepted_at", DATETIME(fsp=6), nullable=True),
        Column("file_id", BIGINT(unsigned=True), nullable=True),
        Column("created_by_user_id", BIGINT(unsigned=True), nullable=False),
        Column("accepted_request_id", BIGINT(unsigned=True), Computed("CASE WHEN status = 'accepted' THEN request_id ELSE NULL END", persisted=True), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        UniqueConstraint("request_id", "revision_number", name="uq_quotations_1"),
        UniqueConstraint("accepted_request_id", name="uq_quotations_2"),
        CheckConstraint("revision_number > 0 AND amount_idr >= 0", name="ck_quotations_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_quotations_1", "quotations", ["file_id"])
    op.create_index("ix_quotations_2", "quotations", ["created_by_user_id"])
    op.create_table(
        "request_documents",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("request_id", BIGINT(unsigned=True), nullable=False),
        Column("document_type", Enum("roof_photo", "electricity_bill", "slo", "pln_permit", "spk", "design", "other"), nullable=False),
        Column("file_id", BIGINT(unsigned=True), nullable=True),
        Column("document_number", String(100), nullable=True),
        Column("status", Enum("pending", "in_progress", "approved", "rejected"), nullable=False, server_default="pending"),
        Column("notes", Text, nullable=True),
        Column("issued_at", DATETIME(fsp=6), nullable=True),
        Column("reviewed_by_user_id", BIGINT(unsigned=True), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_request_documents_1", "request_documents", ["request_id"])
    op.create_index("ix_request_documents_2", "request_documents", ["file_id"])
    op.create_index("ix_request_documents_3", "request_documents", ["reviewed_by_user_id"])
    op.create_table(
        "solar_systems",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("site_id", BIGINT(unsigned=True), nullable=False),
        Column("installation_request_id", BIGINT(unsigned=True), nullable=True, unique=True),
        Column("name", String(255), nullable=False),
        Column("capacity_kwp", Numeric(18, 6), nullable=False),
        Column("panel_count", Integer, nullable=False),
        Column("panel_watt_peak", Integer, nullable=False),
        Column("system_type", Enum("on_grid", "hybrid", "off_grid"), nullable=False),
        Column("status", Enum("planned", "installing", "active", "inactive"), nullable=False, server_default="planned"),
        Column("grid_connection_status", Enum("unconnected", "connected", "disconnected"), nullable=False, server_default="unconnected"),
        Column("installed_at", DATETIME(fsp=6), nullable=True),
        Column("commissioned_at", DATETIME(fsp=6), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("capacity_kwp > 0 AND panel_count > 0 AND panel_watt_peak > 0", name="ck_solar_systems_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_solar_systems_1", "solar_systems", ["site_id"])
    op.create_table(
        "system_financial_profiles",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("system_id", BIGINT(unsigned=True), nullable=False),
        Column("effective_from", DATETIME(fsp=6), nullable=False),
        Column("effective_to", DATETIME(fsp=6), nullable=True),
        Column("import_tariff_idr_per_kwh", Numeric(18, 6), nullable=False),
        Column("export_credit_idr_per_kwh", Numeric(18, 6), nullable=False, server_default=text("0")),
        Column("emission_factor_kg_per_kwh", Numeric(18, 6), nullable=False),
        Column("tree_absorption_kg_per_year", Numeric(18, 6), nullable=False),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        UniqueConstraint("system_id", "effective_from", name="uq_system_financial_profiles_1"),
        CheckConstraint("effective_to IS NULL OR effective_to > effective_from", name="ck_system_financial_profiles_1"),
        CheckConstraint("import_tariff_idr_per_kwh >= 0 AND export_credit_idr_per_kwh >= 0", name="ck_system_financial_profiles_2"),
        CheckConstraint("emission_factor_kg_per_kwh >= 0 AND tree_absorption_kg_per_year > 0", name="ck_system_financial_profiles_3"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "devices",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("device_code", String(50), nullable=False, unique=True),
        Column("system_id", BIGINT(unsigned=True), nullable=False),
        Column("device_type", Enum("inverter", "smart_meter", "solar_array", "battery"), nullable=False),
        Column("serial_number", String(191), nullable=False, unique=True),
        Column("model", String(255), nullable=False),
        Column("firmware_version", String(100), nullable=True),
        Column("status", Enum("normal", "warning", "offline", "unconnected"), nullable=False, server_default="unconnected"),
        Column("last_seen_at", DATETIME(fsp=6), nullable=True),
        Column("expected_interval_seconds", Integer, nullable=False, server_default=text("60")),
        Column("is_active", Boolean, nullable=False, server_default=text("1")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("expected_interval_seconds > 0", name="ck_devices_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_devices_1", "devices", ["status","last_seen_at"])
    op.create_index("ix_devices_2", "devices", ["system_id"])
    op.create_table(
        "device_telemetry",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("device_id", BIGINT(unsigned=True), nullable=False),
        Column("recorded_at", DATETIME(fsp=6), nullable=False),
        Column("received_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("current_power_kw", Numeric(18, 6), nullable=True),
        Column("voltage_v", Numeric(18, 6), nullable=True),
        Column("current_a", Numeric(18, 6), nullable=True),
        Column("grid_frequency_hz", Numeric(18, 6), nullable=True),
        Column("temperature_c", Numeric(18, 6), nullable=True),
        Column("daily_yield_kwh", Numeric(18, 6), nullable=True),
        Column("total_yield_kwh", Numeric(18, 6), nullable=True),
        Column("efficiency_percent", Numeric(18, 6), nullable=True),
        Column("quality_status", Enum("valid", "estimated", "invalid"), nullable=False, server_default="valid"),
        UniqueConstraint("device_id", "recorded_at", name="uq_device_telemetry_1"),
        CheckConstraint("daily_yield_kwh IS NULL OR daily_yield_kwh >= 0", name="ck_device_telemetry_1"),
        CheckConstraint("total_yield_kwh IS NULL OR total_yield_kwh >= 0", name="ck_device_telemetry_2"),
        CheckConstraint("efficiency_percent IS NULL OR (efficiency_percent >= 0 AND efficiency_percent <= 100)", name="ck_device_telemetry_3"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "system_energy_intervals",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("system_id", BIGINT(unsigned=True), nullable=False),
        Column("interval_start_at", DATETIME(fsp=6), nullable=False),
        Column("interval_end_at", DATETIME(fsp=6), nullable=False),
        Column("solar_production_kw", Numeric(18, 6), nullable=True),
        Column("home_consumption_kw", Numeric(18, 6), nullable=True),
        Column("grid_export_kw", Numeric(18, 6), nullable=True),
        Column("grid_import_kw", Numeric(18, 6), nullable=True),
        Column("battery_charge_kw", Numeric(18, 6), nullable=True),
        Column("battery_discharge_kw", Numeric(18, 6), nullable=True),
        Column("production_kwh", Numeric(18, 6), nullable=True),
        Column("consumption_kwh", Numeric(18, 6), nullable=True),
        Column("grid_export_kwh", Numeric(18, 6), nullable=True),
        Column("grid_import_kwh", Numeric(18, 6), nullable=True),
        Column("solar_self_consumed_kwh", Numeric(18, 6), nullable=True),
        Column("quality_status", Enum("valid", "estimated", "incomplete", "invalid"), nullable=False, server_default="valid"),
        UniqueConstraint("system_id", "interval_start_at", name="uq_system_energy_intervals_1"),
        CheckConstraint("interval_end_at > interval_start_at", name="ck_system_energy_intervals_1"),
        CheckConstraint("production_kwh IS NULL OR production_kwh >= 0", name="ck_system_energy_intervals_2"),
        CheckConstraint("consumption_kwh IS NULL OR consumption_kwh >= 0", name="ck_system_energy_intervals_3"),
        CheckConstraint("grid_export_kwh IS NULL OR grid_export_kwh >= 0", name="ck_system_energy_intervals_4"),
        CheckConstraint("grid_import_kwh IS NULL OR grid_import_kwh >= 0", name="ck_system_energy_intervals_5"),
        CheckConstraint("solar_self_consumed_kwh IS NULL OR solar_self_consumed_kwh >= 0", name="ck_system_energy_intervals_6"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "energy_daily_summaries",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("system_id", BIGINT(unsigned=True), nullable=False),
        Column("local_date", Date, nullable=False),
        Column("production_kwh", Numeric(18, 6), nullable=True),
        Column("consumption_kwh", Numeric(18, 6), nullable=True),
        Column("grid_export_kwh", Numeric(18, 6), nullable=True),
        Column("grid_import_kwh", Numeric(18, 6), nullable=True),
        Column("solar_self_consumed_kwh", Numeric(18, 6), nullable=True),
        Column("savings_idr", Numeric(18, 2), nullable=True),
        Column("co2_avoided_kg", Numeric(18, 6), nullable=True),
        Column("peak_power_kw", Numeric(18, 6), nullable=True),
        Column("peak_at", DATETIME(fsp=6), nullable=True),
        Column("coverage_percent", Numeric(5, 2), nullable=True),
        Column("calculation_basis_json", JSON, nullable=False),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        UniqueConstraint("system_id", "local_date", name="uq_energy_daily_summaries_1"),
        CheckConstraint("coverage_percent IS NULL OR (coverage_percent >= 0 AND coverage_percent <= 100)", name="ck_energy_daily_summaries_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "device_alerts",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("device_id", BIGINT(unsigned=True), nullable=False),
        Column("code", String(100), nullable=False),
        Column("level", Enum("info", "warning", "error"), nullable=False),
        Column("message", Text, nullable=False),
        Column("occurred_at", DATETIME(fsp=6), nullable=False),
        Column("resolved_at", DATETIME(fsp=6), nullable=True),
        CheckConstraint("resolved_at IS NULL OR resolved_at >= occurred_at", name="ck_device_alerts_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_device_alerts_1", "device_alerts", ["device_id","occurred_at"])
    op.create_table(
        "device_refresh_jobs",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("device_id", BIGINT(unsigned=True), nullable=False),
        Column("requested_by_user_id", BIGINT(unsigned=True), nullable=False),
        Column("status", Enum("pending", "running", "succeeded", "failed", "timed_out"), nullable=False, server_default="pending"),
        Column("requested_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("completed_at", DATETIME(fsp=6), nullable=True),
        Column("error_message", Text, nullable=True),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_device_refresh_jobs_1", "device_refresh_jobs", ["status","requested_at"])
    op.create_index("ix_device_refresh_jobs_2", "device_refresh_jobs", ["device_id"])
    op.create_index("ix_device_refresh_jobs_3", "device_refresh_jobs", ["requested_by_user_id"])
    op.create_table(
        "maintenance_tasks",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("system_id", BIGINT(unsigned=True), nullable=False),
        Column("technician_id", BIGINT(unsigned=True), nullable=True),
        Column("task_type", String(100), nullable=False),
        Column("scheduled_at", DATETIME(fsp=6), nullable=False),
        Column("completed_at", DATETIME(fsp=6), nullable=True),
        Column("status", Enum("scheduled", "in_progress", "completed", "cancelled"), nullable=False, server_default="scheduled"),
        Column("notes", Text, nullable=True),
        Column("created_by_user_id", BIGINT(unsigned=True), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_maintenance_tasks_1", "maintenance_tasks", ["status","scheduled_at"])
    op.create_index("ix_maintenance_tasks_2", "maintenance_tasks", ["system_id"])
    op.create_index("ix_maintenance_tasks_3", "maintenance_tasks", ["technician_id"])
    op.create_index("ix_maintenance_tasks_4", "maintenance_tasks", ["created_by_user_id"])
    op.create_table(
        "notification_deliveries",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("user_id", BIGINT(unsigned=True), nullable=False),
        Column("system_id", BIGINT(unsigned=True), nullable=True),
        Column("device_alert_id", BIGINT(unsigned=True), nullable=True),
        Column("maintenance_task_id", BIGINT(unsigned=True), nullable=True),
        Column("event_type", Enum("power_drop", "daily_report", "maintenance", "device_alert", "installation_update"), nullable=False),
        Column("channel", Enum("whatsapp", "email", "in_app"), nullable=False),
        Column("title", String(255), nullable=False),
        Column("message", Text, nullable=False),
        Column("scheduled_at", DATETIME(fsp=6), nullable=False),
        Column("sent_at", DATETIME(fsp=6), nullable=True),
        Column("read_at", DATETIME(fsp=6), nullable=True),
        Column("status", Enum("pending", "sending", "sent", "failed", "cancelled"), nullable=False, server_default="pending"),
        Column("attempt_count", Integer, nullable=False, server_default=text("0")),
        Column("provider_message_id", String(255), nullable=True),
        Column("deduplication_key", String(191), nullable=False, unique=True),
        Column("last_error", Text, nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("attempt_count >= 0", name="ck_notification_deliveries_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_notification_deliveries_1", "notification_deliveries", ["status","scheduled_at"])
    op.create_index("ix_notification_deliveries_2", "notification_deliveries", ["user_id","created_at"])
    op.create_index("ix_notification_deliveries_3", "notification_deliveries", ["system_id"])
    op.create_index("ix_notification_deliveries_4", "notification_deliveries", ["device_alert_id"])
    op.create_index("ix_notification_deliveries_5", "notification_deliveries", ["maintenance_task_id"])
    op.create_table(
        "articles",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("slug", String(191), nullable=False, unique=True),
        Column("title", String(255), nullable=False),
        Column("summary", Text, nullable=False),
        Column("content", LONGTEXT, nullable=False),
        Column("category", Enum("Panduan Pemula", "Finansial & ROI", "Teknis & Instalasi", "Regulasi & Kebijakan"), nullable=False),
        Column("author_name", String(255), nullable=False),
        Column("author_user_id", BIGINT(unsigned=True), nullable=True),
        Column("published_at", DATETIME(fsp=6), nullable=True),
        Column("read_time_minutes", Integer, nullable=False),
        Column("cover_file_id", BIGINT(unsigned=True), nullable=True),
        Column("video_embed_url", String(2048), nullable=True),
        Column("is_published", Boolean, nullable=False, server_default=text("0")),
        Column("archived_at", DATETIME(fsp=6), nullable=True),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        CheckConstraint("read_time_minutes > 0", name="ck_articles_1"),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_articles_1", "articles", ["is_published","published_at"])
    op.create_index("ix_articles_2", "articles", ["author_user_id"])
    op.create_index("ix_articles_3", "articles", ["cover_file_id"])
    op.create_table(
        "article_tags",
        Column("article_id", BIGINT(unsigned=True), primary_key=True),
        Column("tag", String(100), primary_key=True),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_article_tags_1", "article_tags", ["tag"])
    op.create_table(
        "faqs",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("question", Text, nullable=False),
        Column("answer", Text, nullable=False),
        Column("category", Enum("Umum", "Kalkulator & Biaya", "Teknis & Atap", "Proses Instalasi", "Garansi & Pemeliharaan"), nullable=False),
        Column("sort_order", Integer, nullable=False, server_default=text("0")),
        Column("is_published", Boolean, nullable=False, server_default=text("0")),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        Column("updated_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_table(
        "audit_logs",
        Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
        Column("actor_user_id", BIGINT(unsigned=True), nullable=True),
        Column("action", String(100), nullable=False),
        Column("entity_type", String(100), nullable=False),
        Column("entity_id", BIGINT(unsigned=True), nullable=False),
        Column("changes_json", JSON, nullable=False),
        Column("created_at", DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)")),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_audit_logs_1", "audit_logs", ["entity_type","entity_id","created_at"])
    op.create_index("ix_audit_logs_2", "audit_logs", ["actor_user_id"])

    # Add foreign keys after creating every table, including files/users cycle.
    op.create_foreign_key("fk_files_uploaded_by_user_id", "files", "users", ["uploaded_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_users_avatar_file_id", "users", "files", ["avatar_file_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_customers_user_id", "customers", "users", ["user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_auth_sessions_user_id", "auth_sessions", "users", ["user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_account_tokens_user_id", "account_tokens", "users", ["user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_notification_preferences_user_id", "notification_preferences", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_sites_customer_id", "sites", "customers", ["customer_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_package_components_package_id", "package_components", "solar_packages", ["package_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_package_items_package_id", "package_items", "solar_packages", ["package_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_solar_calculations_user_id", "solar_calculations", "users", ["user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_solar_calculations_profile_id", "solar_calculations", "calculation_profiles", ["profile_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_installation_requests_customer_id", "installation_requests", "customers", ["customer_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_installation_requests_site_id", "installation_requests", "sites", ["site_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_installation_requests_submitted_by_user_id", "installation_requests", "users", ["submitted_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_installation_requests_calculation_id", "installation_requests", "solar_calculations", ["calculation_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_installation_requests_package_id", "installation_requests", "solar_packages", ["package_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_status_logs_request_id", "request_status_logs", "installation_requests", ["request_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_status_logs_actor_user_id", "request_status_logs", "users", ["actor_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_assignments_request_id", "request_assignments", "installation_requests", ["request_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_assignments_technician_id", "request_assignments", "technicians", ["technician_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_assignments_assigned_by_user_id", "request_assignments", "users", ["assigned_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_appointments_request_id", "request_appointments", "installation_requests", ["request_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_appointments_created_by_user_id", "request_appointments", "users", ["created_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_quotations_request_id", "quotations", "installation_requests", ["request_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_quotations_file_id", "quotations", "files", ["file_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_quotations_created_by_user_id", "quotations", "users", ["created_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_documents_request_id", "request_documents", "installation_requests", ["request_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_documents_file_id", "request_documents", "files", ["file_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_request_documents_reviewed_by_user_id", "request_documents", "users", ["reviewed_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_solar_systems_site_id", "solar_systems", "sites", ["site_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_solar_systems_installation_request_id", "solar_systems", "installation_requests", ["installation_request_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_system_financial_profiles_system_id", "system_financial_profiles", "solar_systems", ["system_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_devices_system_id", "devices", "solar_systems", ["system_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_device_telemetry_device_id", "device_telemetry", "devices", ["device_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_system_energy_intervals_system_id", "system_energy_intervals", "solar_systems", ["system_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_energy_daily_summaries_system_id", "energy_daily_summaries", "solar_systems", ["system_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_device_alerts_device_id", "device_alerts", "devices", ["device_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_device_refresh_jobs_device_id", "device_refresh_jobs", "devices", ["device_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_device_refresh_jobs_requested_by_user_id", "device_refresh_jobs", "users", ["requested_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_maintenance_tasks_system_id", "maintenance_tasks", "solar_systems", ["system_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_maintenance_tasks_technician_id", "maintenance_tasks", "technicians", ["technician_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_maintenance_tasks_created_by_user_id", "maintenance_tasks", "users", ["created_by_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_notification_deliveries_user_id", "notification_deliveries", "users", ["user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_notification_deliveries_system_id", "notification_deliveries", "solar_systems", ["system_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_notification_deliveries_device_alert_id", "notification_deliveries", "device_alerts", ["device_alert_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_notification_deliveries_maintenance_task_id", "notification_deliveries", "maintenance_tasks", ["maintenance_task_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_articles_author_user_id", "articles", "users", ["author_user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_articles_cover_file_id", "articles", "files", ["cover_file_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_article_tags_article_id", "article_tags", "articles", ["article_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_audit_logs_actor_user_id", "audit_logs", "users", ["actor_user_id"], ["id"], ondelete="RESTRICT")


def downgrade() -> None:
    # Explicit downgrade removes data. Never call this as a startup operation.
    op.drop_constraint("fk_audit_logs_actor_user_id", "audit_logs", type_="foreignkey")
    op.drop_constraint("fk_article_tags_article_id", "article_tags", type_="foreignkey")
    op.drop_constraint("fk_articles_author_user_id", "articles", type_="foreignkey")
    op.drop_constraint("fk_articles_cover_file_id", "articles", type_="foreignkey")
    op.drop_constraint("fk_notification_deliveries_user_id", "notification_deliveries", type_="foreignkey")
    op.drop_constraint("fk_notification_deliveries_system_id", "notification_deliveries", type_="foreignkey")
    op.drop_constraint("fk_notification_deliveries_device_alert_id", "notification_deliveries", type_="foreignkey")
    op.drop_constraint("fk_notification_deliveries_maintenance_task_id", "notification_deliveries", type_="foreignkey")
    op.drop_constraint("fk_maintenance_tasks_system_id", "maintenance_tasks", type_="foreignkey")
    op.drop_constraint("fk_maintenance_tasks_technician_id", "maintenance_tasks", type_="foreignkey")
    op.drop_constraint("fk_maintenance_tasks_created_by_user_id", "maintenance_tasks", type_="foreignkey")
    op.drop_constraint("fk_device_refresh_jobs_device_id", "device_refresh_jobs", type_="foreignkey")
    op.drop_constraint("fk_device_refresh_jobs_requested_by_user_id", "device_refresh_jobs", type_="foreignkey")
    op.drop_constraint("fk_device_alerts_device_id", "device_alerts", type_="foreignkey")
    op.drop_constraint("fk_energy_daily_summaries_system_id", "energy_daily_summaries", type_="foreignkey")
    op.drop_constraint("fk_system_energy_intervals_system_id", "system_energy_intervals", type_="foreignkey")
    op.drop_constraint("fk_device_telemetry_device_id", "device_telemetry", type_="foreignkey")
    op.drop_constraint("fk_devices_system_id", "devices", type_="foreignkey")
    op.drop_constraint("fk_system_financial_profiles_system_id", "system_financial_profiles", type_="foreignkey")
    op.drop_constraint("fk_solar_systems_site_id", "solar_systems", type_="foreignkey")
    op.drop_constraint("fk_solar_systems_installation_request_id", "solar_systems", type_="foreignkey")
    op.drop_constraint("fk_request_documents_request_id", "request_documents", type_="foreignkey")
    op.drop_constraint("fk_request_documents_file_id", "request_documents", type_="foreignkey")
    op.drop_constraint("fk_request_documents_reviewed_by_user_id", "request_documents", type_="foreignkey")
    op.drop_constraint("fk_quotations_request_id", "quotations", type_="foreignkey")
    op.drop_constraint("fk_quotations_file_id", "quotations", type_="foreignkey")
    op.drop_constraint("fk_quotations_created_by_user_id", "quotations", type_="foreignkey")
    op.drop_constraint("fk_request_appointments_request_id", "request_appointments", type_="foreignkey")
    op.drop_constraint("fk_request_appointments_created_by_user_id", "request_appointments", type_="foreignkey")
    op.drop_constraint("fk_request_assignments_request_id", "request_assignments", type_="foreignkey")
    op.drop_constraint("fk_request_assignments_technician_id", "request_assignments", type_="foreignkey")
    op.drop_constraint("fk_request_assignments_assigned_by_user_id", "request_assignments", type_="foreignkey")
    op.drop_constraint("fk_request_status_logs_request_id", "request_status_logs", type_="foreignkey")
    op.drop_constraint("fk_request_status_logs_actor_user_id", "request_status_logs", type_="foreignkey")
    op.drop_constraint("fk_installation_requests_customer_id", "installation_requests", type_="foreignkey")
    op.drop_constraint("fk_installation_requests_site_id", "installation_requests", type_="foreignkey")
    op.drop_constraint("fk_installation_requests_submitted_by_user_id", "installation_requests", type_="foreignkey")
    op.drop_constraint("fk_installation_requests_calculation_id", "installation_requests", type_="foreignkey")
    op.drop_constraint("fk_installation_requests_package_id", "installation_requests", type_="foreignkey")
    op.drop_constraint("fk_solar_calculations_user_id", "solar_calculations", type_="foreignkey")
    op.drop_constraint("fk_solar_calculations_profile_id", "solar_calculations", type_="foreignkey")
    op.drop_constraint("fk_package_items_package_id", "package_items", type_="foreignkey")
    op.drop_constraint("fk_package_components_package_id", "package_components", type_="foreignkey")
    op.drop_constraint("fk_sites_customer_id", "sites", type_="foreignkey")
    op.drop_constraint("fk_notification_preferences_user_id", "notification_preferences", type_="foreignkey")
    op.drop_constraint("fk_account_tokens_user_id", "account_tokens", type_="foreignkey")
    op.drop_constraint("fk_auth_sessions_user_id", "auth_sessions", type_="foreignkey")
    op.drop_constraint("fk_customers_user_id", "customers", type_="foreignkey")
    op.drop_constraint("fk_users_avatar_file_id", "users", type_="foreignkey")
    op.drop_constraint("fk_files_uploaded_by_user_id", "files", type_="foreignkey")
    op.drop_table("audit_logs")
    op.drop_table("faqs")
    op.drop_table("article_tags")
    op.drop_table("articles")
    op.drop_table("notification_deliveries")
    op.drop_table("maintenance_tasks")
    op.drop_table("device_refresh_jobs")
    op.drop_table("device_alerts")
    op.drop_table("energy_daily_summaries")
    op.drop_table("system_energy_intervals")
    op.drop_table("device_telemetry")
    op.drop_table("devices")
    op.drop_table("system_financial_profiles")
    op.drop_table("solar_systems")
    op.drop_table("request_documents")
    op.drop_table("quotations")
    op.drop_table("request_appointments")
    op.drop_table("request_assignments")
    op.drop_table("technicians")
    op.drop_table("request_status_logs")
    op.drop_table("installation_requests")
    op.drop_table("solar_calculations")
    op.drop_table("calculation_profiles")
    op.drop_table("package_items")
    op.drop_table("package_components")
    op.drop_table("solar_packages")
    op.drop_table("sites")
    op.drop_table("notification_preferences")
    op.drop_table("account_tokens")
    op.drop_table("auth_sessions")
    op.drop_table("customers")
    op.drop_table("users")
    op.drop_table("files")
