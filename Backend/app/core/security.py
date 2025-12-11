from datetime import datetime, timedelta
from typing import Any, Dict
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(pw: str) -> str:
    return pwd_ctx.hash(pw)

def verify_password(pw: str, pw_hash: str) -> bool:
    return pwd_ctx.verify(pw, pw_hash)

def create_access_token(sub: str, role: str, expires_minutes: int | None = None) -> str:
    exp_min = expires_minutes or settings.JWT_EXPIRES_MIN
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": sub,
        "role": role,
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
        "iat": now,
        "exp": now + timedelta(minutes=exp_min),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
