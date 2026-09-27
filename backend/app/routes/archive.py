"""HTTP endpoints for archive."""
from fastapi import APIRouter, Depends
from typing import Literal
from app.routes.dependencies import admin_user
from app.utils.database import get_db
from app.service import archive as service

router = APIRouter(prefix="/api/v1", tags=["catalog"])

@router.delete("/admin/{resource}/{item_id}")
def archive(resource: Literal["packages", "articles", "faqs"], item_id: int,
            user=Depends(admin_user), db=Depends(get_db)):
    return service.archive(resource, item_id, user, db)
