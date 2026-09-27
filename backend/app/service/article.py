"""Article queries, publication and tagging."""
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, delete
from app.model.content import Article, ArticleTag
from app.model.schemas.article import ArticleInput
from app.utils.cache import read_cached
from app.utils.transactions import commit_with_cache

def article_data(db, row):
    return dict(id=str(row.id), slug=row.slug, title=row.title, summary=row.summary, content=row.content,
        category=row.category, author=row.author_name,
        publishedAt=row.published_at.isoformat() + "Z" if row.published_at else "",
        readTimeMinutes=row.read_time_minutes, coverImage="", videoEmbedUrl=row.video_embed_url,
        isPublished=row.is_published,
        tags=list(db.scalars(select(ArticleTag.tag).where(ArticleTag.article_id == row.id).order_by(ArticleTag.tag))))


def save_article(db, user, data, row):
    from datetime import timezone
    if data.coverImage:
        raise HTTPException(422, "Upload cover integration is not available; leave coverImage empty")
    if any(not tag or len(tag) > 100 for tag in data.tags):
        raise HTTPException(422, "Invalid article tag")
    for key, value in dict(slug=data.slug, title=data.title, summary=data.summary, content=data.content,
        category=data.category, author_name=data.author, author_user_id=user.id,
        read_time_minutes=data.readTimeMinutes, video_embed_url=data.videoEmbedUrl,
        is_published=data.isPublished).items():
        setattr(row, key, value)
    date = data.publishedAt
    row.published_at = (date.astimezone(timezone.utc).replace(tzinfo=None) if date and date.tzinfo else date)
    if data.isPublished and not row.published_at:
        row.published_at = datetime.utcnow()
    db.add(row)
    db.flush()
    db.execute(delete(ArticleTag).where(ArticleTag.article_id == row.id))
    for tag in set(data.tags):
        db.add(ArticleTag(article_id=row.id, tag=tag))
    commit_with_cache(db, "articles")
    return {"id": str(row.id)}


def articles(db):
    return read_cached(db, "articles", "published", 600, lambda: [
        article_data(db, row) for row in db.scalars(select(Article).where(
            Article.is_published.is_(True), Article.archived_at.is_(None))
            .order_by(Article.published_at.desc(), Article.id))])


def admin_articles(user, db):
    # Drafts never enter the shared public cache.
    return [article_data(db, row) for row in db.scalars(select(Article).where(Article.archived_at.is_(None)))]


def create_article(data: ArticleInput, user, db):
    return save_article(db, user, data, Article())


def update_article(item_id: int, data: ArticleInput, user, db):
    row = db.get(Article, item_id)
    if not row:
        raise HTTPException(404)
    return save_article(db, user, data, row)
