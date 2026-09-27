"""HTTP endpoints for energy."""
from fastapi import APIRouter, Depends
from datetime import date
from app.model.schemas.energy import DailyInput
from app.routes.dependencies import current_user, admin_user
from app.utils.database import get_db
from app.service import energy as service

router = APIRouter(prefix="/api/v1", tags=["operations"])

@router.get("/systems/{system_id}/energy")
def energy(system_id: int, start: date, end: date, user=Depends(current_user), db=Depends(get_db)):
    return service.energy(system_id, start, end, user, db)


@router.put("/admin/systems/{system_id}/energy/{local_date}")
def save_daily(system_id: int, local_date: date, data: DailyInput,
               user=Depends(admin_user), db=Depends(get_db)):
    return service.save_daily(system_id, local_date, data, user, db)
