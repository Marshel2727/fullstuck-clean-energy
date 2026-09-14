"""SQLAlchemy models for energy data; DATETIME values use naive UTC."""
from sqlalchemy import (
    CheckConstraint, Column, Date, Enum, ForeignKey, JSON, Numeric, UniqueConstraint, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class SystemFinancialProfile(Base):
    __tablename__ = "system_financial_profiles"
    __table_args__ = (
        UniqueConstraint("system_id", "effective_from", name="uq_system_financial_profiles_1"),
        CheckConstraint("effective_to IS NULL OR effective_to > effective_from", name="ck_system_financial_profiles_1"),
        CheckConstraint("import_tariff_idr_per_kwh >= 0 AND export_credit_idr_per_kwh >= 0", name="ck_system_financial_profiles_2"),
        CheckConstraint("emission_factor_kg_per_kwh >= 0 AND tree_absorption_kg_per_year > 0", name="ck_system_financial_profiles_3"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    system_id = Column(BIGINT(unsigned=True), ForeignKey("solar_systems.id", name="fk_system_financial_profiles_system_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    effective_from = Column(DATETIME(fsp=6), nullable=False)
    effective_to = Column(DATETIME(fsp=6), nullable=True)
    import_tariff_idr_per_kwh = Column(Numeric(18, 6), nullable=False)
    export_credit_idr_per_kwh = Column(Numeric(18, 6), nullable=False, server_default=text("0"))
    emission_factor_kg_per_kwh = Column(Numeric(18, 6), nullable=False)
    tree_absorption_kg_per_year = Column(Numeric(18, 6), nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class SystemEnergyInterval(Base):
    __tablename__ = "system_energy_intervals"
    __table_args__ = (
        UniqueConstraint("system_id", "interval_start_at", name="uq_system_energy_intervals_1"),
        CheckConstraint("interval_end_at > interval_start_at", name="ck_system_energy_intervals_1"),
        CheckConstraint("production_kwh IS NULL OR production_kwh >= 0", name="ck_system_energy_intervals_2"),
        CheckConstraint("consumption_kwh IS NULL OR consumption_kwh >= 0", name="ck_system_energy_intervals_3"),
        CheckConstraint("grid_export_kwh IS NULL OR grid_export_kwh >= 0", name="ck_system_energy_intervals_4"),
        CheckConstraint("grid_import_kwh IS NULL OR grid_import_kwh >= 0", name="ck_system_energy_intervals_5"),
        CheckConstraint("solar_self_consumed_kwh IS NULL OR solar_self_consumed_kwh >= 0", name="ck_system_energy_intervals_6"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    system_id = Column(BIGINT(unsigned=True), ForeignKey("solar_systems.id", name="fk_system_energy_intervals_system_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    interval_start_at = Column(DATETIME(fsp=6), nullable=False)
    interval_end_at = Column(DATETIME(fsp=6), nullable=False)
    solar_production_kw = Column(Numeric(18, 6), nullable=True)
    home_consumption_kw = Column(Numeric(18, 6), nullable=True)
    grid_export_kw = Column(Numeric(18, 6), nullable=True)
    grid_import_kw = Column(Numeric(18, 6), nullable=True)
    battery_charge_kw = Column(Numeric(18, 6), nullable=True)
    battery_discharge_kw = Column(Numeric(18, 6), nullable=True)
    production_kwh = Column(Numeric(18, 6), nullable=True)
    consumption_kwh = Column(Numeric(18, 6), nullable=True)
    grid_export_kwh = Column(Numeric(18, 6), nullable=True)
    grid_import_kwh = Column(Numeric(18, 6), nullable=True)
    solar_self_consumed_kwh = Column(Numeric(18, 6), nullable=True)
    quality_status = Column(Enum("valid", "estimated", "incomplete", "invalid"), nullable=False, server_default="valid")


class EnergyDailySummary(Base):
    __tablename__ = "energy_daily_summaries"
    __table_args__ = (
        UniqueConstraint("system_id", "local_date", name="uq_energy_daily_summaries_1"),
        CheckConstraint("coverage_percent IS NULL OR (coverage_percent >= 0 AND coverage_percent <= 100)", name="ck_energy_daily_summaries_1"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    system_id = Column(BIGINT(unsigned=True), ForeignKey("solar_systems.id", name="fk_energy_daily_summaries_system_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    local_date = Column(Date, nullable=False)
    production_kwh = Column(Numeric(18, 6), nullable=True)
    consumption_kwh = Column(Numeric(18, 6), nullable=True)
    grid_export_kwh = Column(Numeric(18, 6), nullable=True)
    grid_import_kwh = Column(Numeric(18, 6), nullable=True)
    solar_self_consumed_kwh = Column(Numeric(18, 6), nullable=True)
    savings_idr = Column(Numeric(18, 2), nullable=True)
    co2_avoided_kg = Column(Numeric(18, 6), nullable=True)
    peak_power_kw = Column(Numeric(18, 6), nullable=True)
    peak_at = Column(DATETIME(fsp=6), nullable=True)
    coverage_percent = Column(Numeric(5, 2), nullable=True)
    calculation_basis_json = Column(JSON, nullable=False)
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
