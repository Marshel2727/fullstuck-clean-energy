"""FAQ queries and mutations."""
from fastapi import HTTPException
from sqlalchemy import select
from app.model.content import FAQ
from app.model.schemas.faq import FAQInput
from app.utils.cache import read_cached
from app.utils.transactions import commit_with_cache

def faqs(db):
    return read_cached(db, "faqs", "all", 600, lambda: [
        dict(id=str(row.id), question=row.question, answer=row.answer, category=row.category)
        for row in db.scalars(select(FAQ).where(FAQ.is_published.is_(True)).order_by(FAQ.sort_order, FAQ.id))])


def create_faq(data: FAQInput, user, db):
    row = FAQ(**data.model_dump(), is_published=True)
    db.add(row)
    commit_with_cache(db, "faqs")
    return {"id": str(row.id)}


def update_faq(item_id: int, data: FAQInput, user, db):
    row = db.get(FAQ, item_id)
    if not row:
        raise HTTPException(404)
    for key, value in data.model_dump().items():
        setattr(row, key, value)
    commit_with_cache(db, "faqs")
    return {"id": str(row.id)}
