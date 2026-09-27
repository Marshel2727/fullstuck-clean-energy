"""Customer directory queries."""
from sqlalchemy import select
from app.model.user import Customer

def customers(user, db):
    return [dict(id=str(c.id), customerCode=c.customer_code, name=c.name,
                 phone=c.phone, email=c.email, isActive=c.is_active)
            for c in db.scalars(select(Customer).order_by(Customer.id))]
