from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class QuickActionCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    target_route: str
    allowed_roles: str = "student,professor,superuser"
    order_index: int = 0
    active: bool = True


class QuickActionOut(BaseModel):
    id: UUID
    title: str
    subtitle: Optional[str]
    icon: Optional[str]
    target_route: str
    allowed_roles: str
    order_index: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeatureFlagOut(BaseModel):
    key: str
    description: Optional[str]
    value: Optional[dict]
    updated_at: datetime

    class Config:
        from_attributes = True


class FeatureFlagUpdate(BaseModel):
    description: Optional[str] = None
    value: Optional[dict] = None
