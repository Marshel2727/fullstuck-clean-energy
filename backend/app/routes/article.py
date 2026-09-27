"""HTTP endpoints for article."""
from fastapi import APIRouter, Depends
from app.model.schemas.article import ArticleInput
from app.routes.dependencies import admin_user
from app.utils.database import get_db
from app.service import article as service

router = APIRouter(prefix="/api/v1", tags=["catalog"])

@router.get("/articles")
def articles(db=Depends(get_db)):
    return service.articles(db)


@router.get("/admin/articles")
def admin_articles(user=Depends(admin_user), db=Depends(get_db)):
    return service.admin_articles(user, db)


@router.post("/admin/articles")
def create_article(data: ArticleInput, user=Depends(admin_user), db=Depends(get_db)):
    return service.create_article(data, user, db)


@router.put("/admin/articles/{item_id}")
def update_article(item_id: int, data: ArticleInput, user=Depends(admin_user), db=Depends(get_db)):
    return service.update_article(item_id, data, user, db)
