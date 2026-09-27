"""Database commit helper for versioned catalog cache invalidation."""
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from app.utils.cache import bump_epoch

def commit_with_cache(db, namespace):
    bump_epoch(db, namespace)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Data conflicts with an existing record")
