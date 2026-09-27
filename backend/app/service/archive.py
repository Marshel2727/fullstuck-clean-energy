"""Shared archive operation for the existing catalog resource endpoint."""
from datetime import datetime
from typing import Literal
from fastapi import HTTPException
from app.model.package import SolarPackage
from app.model.content import Article, FAQ
from app.utils.transactions import commit_with_cache

def archive(resource: Literal["packages", "articles", "faqs"], item_id: int,
            user, db):
    model = {"packages": SolarPackage, "articles": Article, "faqs": FAQ}[resource]
    row = db.get(model, item_id)
    if not row:
        raise HTTPException(404)
    if resource == "packages":
        row.is_active = False
    elif resource == "articles":
        row.archived_at = datetime.utcnow()
    else:
        row.is_published = False
    commit_with_cache(db, resource)
    return {"ok": True}
