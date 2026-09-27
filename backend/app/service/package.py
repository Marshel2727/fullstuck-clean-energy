"""Package queries, mutations and snapshots."""
from fastapi import HTTPException
from sqlalchemy import select, delete
from app.model.package import SolarPackage, PackageComponent, PackageItem
from app.model.schemas.package import PackageInput
from app.utils.cache import read_cached
from app.utils.transactions import commit_with_cache

PACKAGE_FIELDS = {
    "slug": "slug", "name": "name", "segment": "segment", "capacityKwp": "capacity_kwp",
    "tagline": "tagline", "description": "description", "priceFromIdr": "price_from_idr",
    "estimatedMonthlyProductionKwh": "estimated_monthly_production_kwh",
    "estimatedMonthlySavingsIdr": "estimated_monthly_savings_idr",
    "warrantyPanelsYears": "warranty_panels_years", "warrantyInverterYears": "warranty_inverter_years",
    "warrantyWorkmanshipYears": "warranty_workmanship_years",
    "recommendedRoofAreaSqM": "recommended_roof_area_sqm", "idealFor": "ideal_for", "isPopular": "is_popular",
}

def package_data(db, row):
    data = {key: getattr(row, value) for key, value in PACKAGE_FIELDS.items()}
    data["id"] = str(row.id)
    data["components"] = [dict(name=c.name, specs=c.specs, qty=c.quantity)
        for c in db.scalars(select(PackageComponent).where(PackageComponent.package_id == row.id)
                            .order_by(PackageComponent.sort_order, PackageComponent.id))]
    items = list(db.scalars(select(PackageItem).where(PackageItem.package_id == row.id)
                           .order_by(PackageItem.sort_order, PackageItem.id)))
    for key, kind in [("features", "feature"), ("includedServices", "included_service"), ("exclusions", "exclusion")]:
        data[key] = [item.content for item in items if item.item_type == kind]
    return data


def save_package(db, data, row):
    for key, attr in PACKAGE_FIELDS.items():
        setattr(row, attr, getattr(data, key))
    db.add(row)
    db.flush()
    db.execute(delete(PackageComponent).where(PackageComponent.package_id == row.id))
    db.execute(delete(PackageItem).where(PackageItem.package_id == row.id))
    for i, component in enumerate(data.components):
        db.add(PackageComponent(package_id=row.id, name=component.name, specs=component.specs,
                                quantity=component.qty, sort_order=i))
    for attr, kind in [("features", "feature"), ("includedServices", "included_service"), ("exclusions", "exclusion")]:
        for i, value in enumerate(getattr(data, attr)):
            db.add(PackageItem(package_id=row.id, item_type=kind, content=value, sort_order=i))
    commit_with_cache(db, "packages")
    return {"id": str(row.id)}


def packages(db):
    return read_cached(db, "packages", "all", 600, lambda: [
        package_data(db, row) for row in db.scalars(select(SolarPackage).where(SolarPackage.is_active.is_(True))
                                                  .order_by(SolarPackage.sort_order, SolarPackage.id))])


def create_package(data: PackageInput, user, db):
    return save_package(db, data, SolarPackage())


def update_package(item_id: int, data: PackageInput, user, db):
    row = db.get(SolarPackage, item_id)
    if not row:
        raise HTTPException(404)
    return save_package(db, data, row)
