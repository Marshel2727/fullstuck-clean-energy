"""System ownership checks and system listing."""
from fastapi import HTTPException
from sqlalchemy import select
from app.model.system import SolarSystem, Site
from app.model.user import Customer

def system_for_user(db, user, system_id):
    statement = select(SolarSystem).join(Site, SolarSystem.site_id == Site.id).join(
        Customer, Site.customer_id == Customer.id).where(
        SolarSystem.id == system_id, Site.is_active.is_(True), Customer.is_active.is_(True))
    if user.role != "admin":
        statement = statement.where(Customer.user_id == user.id)
    system = db.scalar(statement)
    if system is None:
        raise HTTPException(404, "System not found")
    return system


def systems(user, db):
    statement = select(SolarSystem).join(Site).join(Customer).where(
        Site.is_active.is_(True), Customer.is_active.is_(True))
    if user.role != "admin":
        statement = statement.where(Customer.user_id == user.id)
    return [dict(id=str(s.id), name=s.name, capacityKwp=s.capacity_kwp)
            for s in db.scalars(statement.order_by(SolarSystem.id))]
