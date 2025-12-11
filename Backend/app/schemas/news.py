from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NewsCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    body: str
    category: str = Field(..., max_length=64)
    tag: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    cta_url: Optional[str] = None
    publish_at: Optional[datetime] = None


class NewsOut(BaseModel):
    id: UUID
    title: str
    subtitle: Optional[str] = None
    body: str
    category: str
    tag: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    cta_url: Optional[str] = None
    published: bool
    publish_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    category: Optional[str] = None
    tag: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    cta_url: Optional[str] = None
    publish_at: Optional[datetime] = None
    published: Optional[bool] = None
