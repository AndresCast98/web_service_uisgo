from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal

bearer = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")
    token = creds.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, ["HS256"], audience=settings.JWT_AUDIENCE, issuer=settings.JWT_ISSUER)
        return payload  # {"sub":..., "role":...}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

def require_role(*roles):
    def inner(user=Depends(current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="forbidden")
        return user
    return inner

require_student   = require_role("student")
require_professor = require_role("professor")
require_superuser = require_role("superuser")
