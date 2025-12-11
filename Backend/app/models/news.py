import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from ..db.base_class import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255))
    body = Column(Text, nullable=False)
    category = Column(String(64), nullable=False)
    tag = Column(String(32), nullable=True)
    image_url = Column(String(512))
    thumbnail_url = Column(String(512))
    hero_image_url = Column(String(512))
    cta_url = Column(String(512))
    published = Column(Boolean, default=False)
    publish_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
