"""SQLAlchemy models for calculation data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Enum, ForeignKey, Index, Integer, JSON, Numeric, String, UniqueConstraint, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class CalculationProfile(Base):
    __tablename__ = "calculation_profiles"
    __table_args__ = (
        CheckConstraint("sun_hours_per_day > 0 AND sun_hours_per_day <= 24", name="ck_calculation_profiles_1"),
        CheckConstraint("system_efficiency > 0 AND system_efficiency <= 1", name="ck_calculation_profiles_2"),
        CheckConstraint("panel_watt_peak > 0 AND area_per_panel_sqm > 0", name="ck_calculation_profiles_3"),
        CheckConstraint("cost_per_kwp_min_idr >= 0 AND cost_per_kwp_max_idr >= cost_per_kwp_min_idr", name="ck_calculation_profiles_4"),
        CheckConstraint("emission_factor >= 0 AND tree_absorption_kg_per_year > 0", name="ck_calculation_profiles_5"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    version = Column(String(50), nullable=False, unique=True)
    sun_hours_per_day = Column(Numeric(18, 6), nullable=False)
    system_efficiency = Column(Numeric(18, 6), nullable=False)
    panel_watt_peak = Column(Integer, nullable=False)
    area_per_panel_sqm = Column(Numeric(18, 6), nullable=False)
    cost_per_kwp_min_idr = Column(Numeric(18, 2), nullable=False)
    cost_per_kwp_max_idr = Column(Numeric(18, 2), nullable=False)
    emission_factor = Column(Numeric(18, 6), nullable=False)
    tree_absorption_kg_per_year = Column(Numeric(18, 6), nullable=False)
    tariff_rules_json = Column(JSON, nullable=False)
    effective_from = Column(DATETIME(fsp=6), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class SolarCalculation(Base):
    __tablename__ = "solar_calculations"
    __table_args__ = (
        UniqueConstraint("access_token_hash", name="uq_solar_calculations_1"),
        CheckConstraint("monthly_kwh >= 0 AND monthly_bill_idr >= 0", name="ck_solar_calculations_1"),
        CheckConstraint("pln_power_va > 0 AND roof_area_sqm > 0", name="ck_solar_calculations_2"),
        CheckConstraint("target_coverage_percent > 0 AND target_coverage_percent <= 100", name="ck_solar_calculations_3"),
        Index("ix_solar_calculations_1", "user_id", "created_at"),
        Index("ix_solar_calculations_2", "profile_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_solar_calculations_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    profile_id = Column(BIGINT(unsigned=True), ForeignKey("calculation_profiles.id", name="fk_solar_calculations_profile_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    access_token_hash = Column(String(64), nullable=True)
    expires_at = Column(DATETIME(fsp=6), nullable=True)
    city = Column(String(100), nullable=False)
    property_type = Column(Enum("household", "business", "industry", "school", "other"), nullable=False)
    monthly_kwh = Column(Numeric(18, 6), nullable=False)
    monthly_bill_idr = Column(Numeric(18, 2), nullable=False)
    pln_power_va = Column(Integer, nullable=False)
    roof_area_sqm = Column(Numeric(18, 6), nullable=False)
    roof_orientation = Column(Enum("utara", "selatan", "timur", "barat", "optimal"), nullable=True)
    shading_condition = Column(Enum("none", "partial", "heavy"), nullable=True)
    target_coverage_percent = Column(Numeric(5, 2), nullable=False)
    result_json = Column(JSON, nullable=False)
    assumptions_json = Column(JSON, nullable=False)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
