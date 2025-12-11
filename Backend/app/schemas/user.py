from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
    role: Role = Role.professor

    @field_validator("role")
    @classmethod
    def only_admin_roles(cls, value: Role) -> Role:
        if value == Role.student:
            raise ValueError("role must be professor or superuser")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: Role
    active: bool | None = True
    created_at: datetime
    coins_balance: int = 0
    question_credits: int = 0
    questions_answered: int = 0
    level: int = 1
    xp_progress: float = 0.0
    xp_to_next: int = 100


class UserUpdate(BaseModel):
    full_name: str
