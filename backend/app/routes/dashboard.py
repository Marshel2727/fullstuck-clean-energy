"""HTTP endpoints for dashboard."""
from fastapi import APIRouter, Depends
from app.routes.dependencies import current_user
from app.utils.database import get_db
from app.service import dashboard as service

router = APIRouter(prefix="/api/v1", tags=["operations"])

@router.get("/systems/{system_id}/dashboard")
def dashboard(system_id: int, user=Depends(current_user), db=Depends(get_db)):
    return service.dashboard(system_id, user, db)
