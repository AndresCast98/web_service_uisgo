from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CoinBalance(BaseModel):
    balance: int = 0
    last_updated: datetime


class CoinLedgerEntry(BaseModel):
    id: UUID
    delta: int
    reason: str
    activity_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CoinAdjustIn(BaseModel):
    user_id: UUID
    delta: int = Field(..., description="Cantidad positiva o negativa de coins")
    reason: str = Field(..., max_length=120)
    activity_id: Optional[UUID] = None
