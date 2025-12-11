import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ..db.base_class import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    kind = Column(String(32), nullable=False, default="store", index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    description = Column(Text)
    thumbnail_url = Column(String(512))
    hero_image_url = Column(String(512))
    location = Column(JSONB)
    contact = Column(JSONB)
    tags = Column(JSONB, default=list)
    is_public = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    status = Column(String(32), nullable=False, default="active", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlaceProduct(Base):
    __tablename__ = "place_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(scale=2))
    image_url = Column(String(512))
    cta_url = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
    order_index = Column(Numeric(scale=2), default=0)


class MapEvent(Base):
    __tablename__ = "map_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(255))
    description = Column(Text)
    category = Column(String(64), nullable=False, index=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    location = Column(JSONB)
    contact = Column(JSONB)
    banner_url = Column(String(512))
    is_featured = Column(Boolean, default=False)
    visibility = Column(String(32), nullable=False, default="public", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
