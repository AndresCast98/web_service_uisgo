from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

class ActivityCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str = "quiz_single"
    q_text: str
    q_type: str = "single"
    q_options: Optional[List[str]] = None
    q_correct: Optional[List[int]] = None
    coins_on_complete: int = 0
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    target_group_ids: List[UUID]

class AnswerIn(BaseModel):
    selected: Optional[List[int]] = None
    text: Optional[str] = None


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str] = None
    type: str
    status: str
    coins_on_complete: int
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    created_at: datetime


class ActivityTargetOut(BaseModel):
    id: UUID
    name: str


class ActivitySubmissionOut(BaseModel):
    id: UUID
    student_id: UUID
    student_name: Optional[str] = None
    student_email: EmailStr
    status: str
    is_correct: Optional[bool] = None
    awarded_coins: Optional[int] = None
    answer: Optional[dict[str, Any]] = None
    submitted_at: datetime


class ActivityDetailOut(ActivityOut):
    q_text: str
    q_options: Optional[List[str]] = None
    q_correct: Optional[List[int]] = None
    target_groups: List[ActivityTargetOut]
    submissions: List[ActivitySubmissionOut]
