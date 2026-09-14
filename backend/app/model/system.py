"""SQLAlchemy models for system data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Enum, ForeignKey, Index, Integer, Numeric, String, Text, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME

from app.model.base import Base


class Site(Base):
    __tablename__ = "sites"
    __table_args__ = (
        CheckConstraint("pln_power_va > 0", name="ck_sites_1"),
        CheckConstraint("roof_area_sqm >= 0", name="ck_sites_2"),
        Index("ix_sites_1", "customer_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    customer_id = Column(BIGINT(unsigned=True), ForeignKey("customers.id", name="fk_sites_customer_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(12), nullable=True)
    property_type = Column(Enum("household", "business", "industry", "school", "other"), nullable=False)
    pln_power_va = Column(Integer, nullable=False)
    roof_area_sqm = Column(Numeric(18, 6), nullable=False)
    roof_type = Column(Enum("genteng", "dak_beton", "spandek_metal", "asbes", "other"), nullable=True)
    roof_orientation = Column(Enum("utara", "selatan", "timur", "barat", "optimal"), nullable=True)
    shading_condition = Column(Enum("none", "partial", "heavy"), nullable=True)
    timezone = Column(String(64), nullable=False, server_default="Asia/Jakarta")
    is_active = Column(Boolean, nullable=False, server_default=text("1"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class SolarSystem(Base):
    __tablename__ = "solar_systems"
    __table_args__ = (
        CheckConstraint("capacity_kwp > 0 AND panel_count > 0 AND panel_watt_peak > 0", name="ck_solar_systems_1"),
        Index("ix_solar_systems_1", "site_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    site_id = Column(BIGINT(unsigned=True), ForeignKey("sites.id", name="fk_solar_systems_site_id", ondelete="RESTRICT", use_alter=True), nullable=False)
    installation_request_id = Column(BIGINT(unsigned=True), ForeignKey("installation_requests.id", name="fk_solar_systems_installation_request_id", ondelete="RESTRICT", use_alter=True), nullable=True, unique=True)
    name = Column(String(255), nullable=False)
    capacity_kwp = Column(Numeric(18, 6), nullable=False)
    panel_count = Column(Integer, nullable=False)
    panel_watt_peak = Column(Integer, nullable=False)
    system_type = Column(Enum("on_grid", "hybrid", "off_grid"), nullable=False)
    status = Column(Enum("planned", "installing", "active", "inactive"), nullable=False, server_default="planned")
    grid_connection_status = Column(Enum("unconnected", "connected", "disconnected"), nullable=False, server_default="unconnected")
    installed_at = Column(DATETIME(fsp=6), nullable=True)
    commissioned_at = Column(DATETIME(fsp=6), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
