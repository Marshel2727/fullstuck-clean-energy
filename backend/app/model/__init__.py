"""Register all feature models on the shared Base metadata.

Import this package before Alembic inspects metadata. Domain files reference other
tables through string foreign keys, so they do not import each other.
"""
from app.model.base import Base
from app.model.user import User, Customer, AuthSession, AccountToken
from app.model.file import StoredFile
from app.model.package import SolarPackage, PackageComponent, PackageItem
from app.model.calculation import CalculationProfile, SolarCalculation
from app.model.installation import InstallationRequest, RequestStatusLog, RequestAssignment, RequestAppointment, Quotation, RequestDocument
from app.model.system import Site, SolarSystem
from app.model.device import Device, DeviceTelemetry, DeviceAlert, DeviceRefreshJob
from app.model.energy import SystemFinancialProfile, SystemEnergyInterval, EnergyDailySummary
from app.model.maintenance import Technician, MaintenanceTask
from app.model.notification import NotificationPreference, NotificationDelivery
from app.model.content import Article, ArticleTag, FAQ
from app.model.audit import AuditLog
from app.model.cache import CacheEpoch

__all__ = [
    "Base",
    "User",
    "Customer",
    "AuthSession",
    "AccountToken",
    "StoredFile",
    "SolarPackage",
    "PackageComponent",
    "PackageItem",
    "CalculationProfile",
    "SolarCalculation",
    "InstallationRequest",
    "RequestStatusLog",
    "RequestAssignment",
    "RequestAppointment",
    "Quotation",
    "RequestDocument",
    "Site",
    "SolarSystem",
    "Device",
    "DeviceTelemetry",
    "DeviceAlert",
    "DeviceRefreshJob",
    "SystemFinancialProfile",
    "SystemEnergyInterval",
    "EnergyDailySummary",
    "Technician",
    "MaintenanceTask",
    "NotificationPreference",
    "NotificationDelivery",
    "Article",
    "ArticleTag",
    "FAQ",
    "AuditLog",
    "CacheEpoch",
]
