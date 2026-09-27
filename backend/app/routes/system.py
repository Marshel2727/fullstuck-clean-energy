"""HTTP endpoints for system."""
from fastapi import APIRouter, Depends
from app.routes.dependencies import current_user
from app.utils.database import get_db
from app.service import system as service

router = APIRouter(prefix="/api/v1", tags=["operations"])

@router.get("/systems")
def systems(user=Depends(current_user), db=Depends(get_db)):
    return service.systems(user, db)
