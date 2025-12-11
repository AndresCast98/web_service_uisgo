from typing import Literal

from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    role: Literal["professor", "communications", "market_manager"] | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    email: EmailStr
    full_name: str | None = None


class ForgotPasswordOut(BaseModel):
    message: str
    reset_token: str | None = None
