from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PlaceBase(BaseModel):
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    location: Optional[dict] = None
    contact: Optional[dict] = None
    tags: List[str] = Field(default_factory=list)
    is_public: bool = True


class PlaceCreate(PlaceBase):
    name: str
    category: str
    kind: str = "store"


class PlaceUpdate(PlaceBase):
    name: Optional[str] = None
    category: Optional[str] = None
    kind: Optional[str] = None
    is_verified: Optional[bool] = None
    status: Optional[str] = None


class PlaceOut(BaseModel):
    id: UUID
    owner_id: UUID
    kind: str
    name: str
    category: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    hero_image_url: Optional[str]
    location: Optional[dict]
    contact: Optional[dict]
    tags: Optional[list]
    is_public: bool
    is_verified: bool
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaceProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    cta_url: Optional[str] = None
    order_index: Optional[float] = 0


class PlaceProductOut(BaseModel):
    id: UUID
    place_id: UUID
    name: str
    description: Optional[str]
    price: Optional[float]
    image_url: Optional[str]
    cta_url: Optional[str]
    order_index: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class MapEventCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    category: str
    start_at: datetime
    end_at: datetime
    location: Optional[dict] = None
    contact: Optional[dict] = None
    banner_url: Optional[str] = None
    visibility: str = "public"
    place_id: Optional[UUID] = None


class MapEventUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location: Optional[dict] = None
    contact: Optional[dict] = None
    banner_url: Optional[str] = None
    visibility: Optional[str] = None
    place_id: Optional[UUID] = None
    is_featured: Optional[bool] = None


class MapEventOut(BaseModel):
    id: UUID
    owner_id: UUID
    place_id: Optional[UUID]
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    category: str
    start_at: datetime
    end_at: datetime
    location: Optional[dict]
    contact: Optional[dict]
    banner_url: Optional[str]
    visibility: str
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
