from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WellnessPromptCreate(BaseModel):
    title: str
    description: Optional[str] = None
    options: List[str] = Field(..., min_length=1)
    screen: str
    frequency: str = "daily"
    active: bool = True


class WellnessPromptOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    options: List[str]
    screen: str
    frequency: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RecordMoodIn(BaseModel):
    prompt_id: UUID
    mood_value: str
    metadata: Optional[dict] = None


class UserMoodOut(BaseModel):
    id: UUID
    prompt_id: UUID
    mood_value: str
    recorded_at: datetime

    class Config:
        from_attributes = True


class WellnessCenterCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[dict] = None
    contact: Optional[dict] = None


class WellnessCenterOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    location: Optional[dict]
    contact: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class CreateTurnIn(BaseModel):
    center_id: UUID
    scheduled_at: datetime


class WellnessTurnOut(BaseModel):
    id: UUID
    center_id: UUID
    user_id: UUID
    scheduled_at: datetime
    status: str
    qr_token: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
