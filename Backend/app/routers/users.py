from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role, require_superuser
from app.core.security import hash_password
from app.models.coins import CoinsLedger
from app.models.question import QuestionCredit, QuestionResponse
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications", "market_manager")


@router.get("/me", response_model=UserOut)
def get_current_user(user=Depends(require_any_user), db: Session = Depends(get_db)) -> UserOut:
    current = db.get(User, user["sub"])
    if not current:
        raise HTTPException(status_code=404, detail="user not found")

    coins_balance = (
        db.query(func.coalesce(func.sum(CoinsLedger.delta), 0))
        .filter(CoinsLedger.user_id == current.id)
        .scalar()
        or 0
    )
    question_credits = (
        db.query(QuestionCredit.balance).filter(QuestionCredit.user_id == current.id).scalar() or 0
    )
    questions_answered = (
        db.query(func.count(QuestionResponse.id))
        .filter(QuestionResponse.user_id == current.id)
        .scalar()
        or 0
    )
    total_xp = coins_balance + questions_answered * 10
    level = max(1, (total_xp // 100) + 1)
    xp_in_level = total_xp % 100
    xp_progress = xp_in_level / 100 if level > 0 else 0.0
    xp_to_next = 100 - xp_in_level if xp_in_level > 0 else 100

    base = UserOut.model_validate(current)
    return base.model_copy(
        update={
            "coins_balance": coins_balance,
            "question_credits": question_credits,
            "questions_answered": questions_answered,
            "level": level,
            "xp_progress": xp_progress,
            "xp_to_next": xp_to_next,
        }
    )


@router.post(
    "/",
    response_model=UserOut,
    status_code=201,
    dependencies=[Depends(require_superuser)],
)
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> User:
    exists = db.query(User).filter(User.email == body.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="email already registered")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/me", response_model=UserOut)
def update_current_user(
    body: UserUpdate,
    user=Depends(require_role("professor", "superuser")),
    db: Session = Depends(get_db),
) -> UserOut:
    current = db.get(User, user["sub"])
    if not current:
        raise HTTPException(status_code=404, detail="user not found")

    current.full_name = body.full_name
    db.commit()
    db.refresh(current)
    return current
