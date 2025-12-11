from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class ChatSessionCreate(BaseModel):
    title: str


class ChatSessionOut(BaseModel):
    id: UUID
    title: str
    coins_spent: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str
    attachments: Optional[List[str]] = None


class ChatMessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    attachments: Optional[List[str]]
    coins_delta: int
    created_at: datetime

    class Config:
        from_attributes = True
