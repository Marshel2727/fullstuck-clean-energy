"""SQLAlchemy models for content data; DATETIME values use naive UTC."""
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Enum, ForeignKey, Index, Integer, String, Text, text,
)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, LONGTEXT

from app.model.base import Base


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        CheckConstraint("read_time_minutes > 0", name="ck_articles_1"),
        Index("ix_articles_1", "is_published", "published_at"),
        Index("ix_articles_2", "author_user_id"),
        Index("ix_articles_3", "cover_file_id"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    slug = Column(String(191), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(LONGTEXT, nullable=False)
    category = Column(Enum("Panduan Pemula", "Finansial & ROI", "Teknis & Instalasi", "Regulasi & Kebijakan"), nullable=False)
    author_name = Column(String(255), nullable=False)
    author_user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id", name="fk_articles_author_user_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    published_at = Column(DATETIME(fsp=6), nullable=True)
    read_time_minutes = Column(Integer, nullable=False)
    cover_file_id = Column(BIGINT(unsigned=True), ForeignKey("files.id", name="fk_articles_cover_file_id", ondelete="RESTRICT", use_alter=True), nullable=True)
    video_embed_url = Column(String(2048), nullable=True)
    is_published = Column(Boolean, nullable=False, server_default=text("0"))
    archived_at = Column(DATETIME(fsp=6), nullable=True)
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))


class ArticleTag(Base):
    __tablename__ = "article_tags"
    __table_args__ = (
        Index("ix_article_tags_1", "tag"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    article_id = Column(BIGINT(unsigned=True), ForeignKey("articles.id", name="fk_article_tags_article_id", ondelete="CASCADE", use_alter=True), primary_key=True)
    tag = Column(String(100), primary_key=True)


class FAQ(Base):
    __tablename__ = "faqs"
    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(Enum("Umum", "Kalkulator & Biaya", "Teknis & Atap", "Proses Instalasi", "Garansi & Pemeliharaan"), nullable=False)
    sort_order = Column(Integer, nullable=False, server_default=text("0"))
    is_published = Column(Boolean, nullable=False, server_default=text("0"))
    created_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"))
    updated_at = Column(DATETIME(fsp=6), nullable=False, server_default=text("CURRENT_TIMESTAMP(6)"), onupdate=text("CURRENT_TIMESTAMP(6)"))
