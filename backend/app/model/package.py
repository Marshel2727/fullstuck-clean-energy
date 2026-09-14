"""SQLAlchemy models for package data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Enum, ForeignKey, Index, Integer, Numeric, String, Text, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class SolarPackage(Base):
    __tablename__ = "solar_packages"
    __table_args__ = (
        CheckConstraint("capacity_kwp > 0", name="ck_solar_packages_1"),
        CheckConstraint("price_from_idr >= 0", name="ck_solar_packages_2"),
        CheckConstraint("estimated_monthly_production_kwh >= 0", name="ck_solar_packages_3"),
        CheckConstraint("estimated_monthly_savings_idr >= 0", name="ck_solar_packages_4"),
        CheckConstraint("recommended_roof_area_sqm >= 0", name="ck_solar_packages_5"),
        CheckConstraint("warranty_panels_years >= 0 AND warranty_inverter_years >= 0 AND warranty_workmanship_years >= 0", name="ck_solar_packages_6"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    slug = Column(String(191), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    segment = Column(Enum("household", "business", "industry", "school", "other"), nullable=False)
    capacity_kwp = Column(Numeric(18, 6), nullable=False)
    tagline = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price_from_idr = Column(Numeric(18, 2), nullable=False)
    estimated_monthly_production_kwh = Column(Numeric(18, 6), nullable=False)
    estimated_monthly_savings_idr = Column(Numeric(18, 2), nullable=False)
    warranty_panels_years = Column(Integer, nullable=False)
    warranty_inverter_years = Column(Integer, nullable=False)
    warranty_workmanship_years = Column(Integer, nullable=False)
    recommended_roof_area_sqm = Column(Numeric(18, 6), nullable=False)
    ideal_for = Column(Text, nullable=False)
    is_popular = Column(Boolean, nullable=False, server_default=text("0"))
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    sort_order = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class PackageComponent(Base):
    __tablename__ = "package_components"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_package_components_1"),
        Index("ix_package_components_1", "package_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    package_id = Column(BIGINT(unsigned=True), ForeignKey("solar_packages.id", name="fk_package_components_package_id", ondelete="CASCADE", use_alter=True), nullable=False)
    name = Column(String(255), nullable=False)
    specs = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    sort_order = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class PackageItem(Base):
    __tablename__ = "package_items"
    __table_args__ = (
        Index("ix_package_items_1", "package_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    package_id = Column(BIGINT(unsigned=True), ForeignKey("solar_packages.id", name="fk_package_items_package_id", ondelete="CASCADE", use_alter=True), nullable=False)
    item_type = Column(Enum("feature", "included_service", "exclusion"), nullable=False)
    content = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False, server_default=text("0"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
