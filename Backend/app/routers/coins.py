from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.coins import CoinsLedger
from app.models.user import User
from app.schemas.coins import CoinAdjustIn, CoinBalance, CoinLedgerEntry

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications")


def _fetch_user(db: Session, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return user


@router.get("/me", response_model=CoinBalance)
def my_balance(user=Depends(require_any_user), db: Session = Depends(get_db)) -> CoinBalance:
    total = (
        db.query(func.coalesce(func.sum(CoinsLedger.delta), 0))
        .filter(CoinsLedger.user_id == user["sub"])
        .scalar()
        or 0
    )
    last_row = (
        db.query(CoinsLedger.created_at)
        .filter(CoinsLedger.user_id == user["sub"])
        .order_by(CoinsLedger.created_at.desc())
        .first()
    )
    last_updated = last_row.created_at if last_row else datetime.utcnow()
    return CoinBalance(balance=total, last_updated=last_updated)


@router.get("/me/ledger", response_model=List[CoinLedgerEntry])
def my_ledger(
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[CoinLedgerEntry]:
    rows = (
        db.query(CoinsLedger)
        .filter(CoinsLedger.user_id == user["sub"])
        .order_by(CoinsLedger.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return rows


@router.post("/adjust", response_model=CoinLedgerEntry, status_code=status.HTTP_201_CREATED)
def adjust_balance(
    body: CoinAdjustIn,
    _: dict = Depends(require_role("superuser")),
    db: Session = Depends(get_db),
) -> CoinLedgerEntry:
    _fetch_user(db, body.user_id)
    entry = CoinsLedger(
        user_id=body.user_id,
        delta=body.delta,
        reason=body.reason,
        activity_id=body.activity_id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
