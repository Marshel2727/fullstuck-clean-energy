from datetime import datetime
from typing import Literal
from pydantic import Field, field_validator
from app.model.schemas.common import Payload

class ArticleInput(Payload):
    @field_validator("publishedAt", mode="before")
    @classmethod
    def blank_date(cls, value):
        return None if value == "" else value

    slug: str = Field(min_length=1, max_length=191, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=1, max_length=255)
    summary: str
    content: str
    category: Literal["Panduan Pemula", "Finansial & ROI", "Teknis & Instalasi", "Regulasi & Kebijakan"]
    author: str = Field(min_length=1, max_length=255)
    publishedAt: datetime | None = None
    readTimeMinutes: int = Field(gt=0)
    tags: list[str] = Field(default_factory=list, max_length=100)
    isPublished: bool = False
    # Existing frontend URLs are not trusted storage keys. Upload integration is separate.
    coverImage: str = ""
    videoEmbedUrl: str | None = Field(default=None, max_length=2048)
