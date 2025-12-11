from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class QuestionGroupOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class QuestionCreate(BaseModel):
    title: str
    body: str
    category: str = Field(..., max_length=64)
    type: str = Field(default="open")
    options: Optional[List[str]] = None
    reward_credits: int = 0
    reward_coins: int = 0
    group_ids: List[UUID] = Field(..., min_length=1)


class QuestionOut(BaseModel):
    id: UUID
    title: str
    body: str
    category: str
    type: str
    options: Optional[List[str]] = None
    reward_credits: int
    reward_coins: int
    active: bool
    created_at: datetime
    groups: List[QuestionGroupOut] = Field(default_factory=list)
    is_global: bool = True

    class Config:
        from_attributes = True


class QuestionAnswerIn(BaseModel):
    answer: Optional[Any] = None


class QuestionAnswerOut(BaseModel):
    question_id: UUID
    credits_awarded: int
    coins_awarded: int
    new_credit_balance: int


class QuestionCreditsOut(BaseModel):
    balance: int
    required_for_chat: int = 50
    last_updated: datetime


class QuestionTargetsUpdate(BaseModel):
    group_ids: List[UUID] = Field(..., min_length=1)


class QuestionResponseItem(BaseModel):
    id: UUID
    question_id: UUID
    question_title: str
    student_email: EmailStr
    student_name: Optional[str] = None
    answer: Optional[Any] = None
    credits_awarded: int
    coins_awarded: int
    created_at: datetime
    groups: List[QuestionGroupOut] = Field(default_factory=list)
    is_global: bool = True
