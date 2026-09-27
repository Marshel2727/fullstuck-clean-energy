from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.service import health as service
from app.utils.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return service.health()


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:
    return service.readiness(db)
