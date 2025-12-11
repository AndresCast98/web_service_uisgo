from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GroupCreate(BaseModel):
    name: str
    subject: Optional[str] = None


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None


class GroupOut(BaseModel):
    id: UUID
    name: str
    subject: Optional[str] = None
    created_at: datetime
    student_count: int
    owner_email: EmailStr
    owner_name: Optional[str] = None


class GroupQuestionSummary(BaseModel):
    id: UUID
    title: str
    category: str
    reward_credits: int


class GroupDetail(GroupOut):
    invite_code: Optional[str] = None
    web_join: Optional[str] = None
    deep_link: Optional[str] = None
    qr_png: Optional[str] = None
    questions: list[GroupQuestionSummary] = Field(default_factory=list)


class InviteCreate(BaseModel):
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None


class JoinByCode(BaseModel):
    code: str
