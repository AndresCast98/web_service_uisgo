import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.password_reset import PasswordResetToken
from app.models.user import Role, User
from app.schemas.auth import (
    ForgotPasswordIn,
    ForgotPasswordOut,
    LoginIn,
    RegisterIn,
    TokenOut,
)

router = APIRouter()


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == body.email).first()
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=400, detail="invalid credentials")
    token = create_access_token(str(u.id), u.role.value)
    return TokenOut(access_token=token, role=u.role.value, email=u.email, full_name=u.full_name)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def forgot_password(body: ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    message = "Si el correo está registrado enviaremos instrucciones para restablecer la contraseña."

    if not user:
        return ForgotPasswordOut(message=message)

    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used.is_(False),
        PasswordResetToken.expires_at > datetime.utcnow(),
    ).update({"used": True})

    token_value = secrets.token_urlsafe(32)
    expires_at = PasswordResetToken.expires_after(settings.PASSWORD_RESET_TOKEN_MINUTES)
    reset = PasswordResetToken(user_id=user.id, token=token_value, expires_at=expires_at)
    db.add(reset)
    db.commit()
    db.refresh(reset)

    return ForgotPasswordOut(message=message, reset_token=token_value)


def _create_user(body: RegisterIn, db: Session, role: Role) -> User:
    exists = db.query(User).filter(User.email == body.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _token_response(user: User) -> TokenOut:
    token = create_access_token(str(user.id), user.role.value)
    return TokenOut(
        access_token=token,
        role=user.role.value,
        email=user.email,
        full_name=user.full_name,
    )


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    selected_role = Role(body.role) if body.role else Role.professor
    user = _create_user(body, db, selected_role)
    return _token_response(user)


@router.post(
    "/register/student",
    response_model=TokenOut,
    status_code=status.HTTP_201_CREATED,
)
def register_student(body: RegisterIn, db: Session = Depends(get_db)):
    user = _create_user(body, db, Role.student)
    return _token_response(user)
