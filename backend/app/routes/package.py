"""HTTP endpoints for package."""
from fastapi import APIRouter, Depends
from app.model.schemas.package import PackageInput
from app.routes.dependencies import admin_user
from app.utils.database import get_db
from app.service import package as service

router = APIRouter(prefix="/api/v1", tags=["catalog"])

@router.get("/packages")
def packages(db=Depends(get_db)):
    return service.packages(db)


@router.post("/admin/packages")
def create_package(data: PackageInput, user=Depends(admin_user), db=Depends(get_db)):
    return service.create_package(data, user, db)


@router.put("/admin/packages/{item_id}")
def update_package(item_id: int, data: PackageInput, user=Depends(admin_user), db=Depends(get_db)):
    return service.update_package(item_id, data, user, db)
