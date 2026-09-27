"""HTTP endpoints for faq."""
from fastapi import APIRouter, Depends
from app.model.schemas.faq import FAQInput
from app.routes.dependencies import admin_user
from app.utils.database import get_db
from app.service import faq as service

router = APIRouter(prefix="/api/v1", tags=["catalog"])

@router.get("/faqs")
def faqs(db=Depends(get_db)):
    return service.faqs(db)


@router.post("/admin/faqs")
def create_faq(data: FAQInput, user=Depends(admin_user), db=Depends(get_db)):
    return service.create_faq(data, user, db)


@router.put("/admin/faqs/{item_id}")
def update_faq(item_id: int, data: FAQInput, user=Depends(admin_user), db=Depends(get_db)):
    return service.update_faq(item_id, data, user, db)
