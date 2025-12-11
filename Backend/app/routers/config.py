from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.quick_actions import FeatureFlag, QuickAction
from app.schemas.quick_actions import (
    FeatureFlagOut,
    FeatureFlagUpdate,
    QuickActionCreate,
    QuickActionOut,
)

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications")
require_superuser = require_role("superuser")


@router.get("/quick-actions", response_model=List[QuickActionOut])
def get_active_quick_actions(user=Depends(require_any_user), db: Session = Depends(get_db)) -> List[QuickActionOut]:
    role = user.get("role")
    return (
        db.query(QuickAction)
        .filter(QuickAction.active.is_(True))
        .filter(QuickAction.allowed_roles.ilike(f"%{role}%"))
        .order_by(QuickAction.order_index.asc())
        .all()
    )


@router.post("/quick-actions", response_model=QuickActionOut, status_code=status.HTTP_201_CREATED)
def create_quick_action(
    body: QuickActionCreate,
    _: dict = Depends(require_superuser),
    db: Session = Depends(get_db),
) -> QuickActionOut:
    action = QuickAction(**body.model_dump())
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@router.patch("/quick-actions/{action_id}", response_model=QuickActionOut)
def update_quick_action(
    action_id: UUID,
    body: QuickActionCreate,
    _: dict = Depends(require_superuser),
    db: Session = Depends(get_db),
) -> QuickActionOut:
    action = db.get(QuickAction, action_id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="quick action not found")
    for field, value in body.model_dump().items():
        setattr(action, field, value)
    db.commit()
    db.refresh(action)
    return action


@router.delete("/quick-actions/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quick_action(
    action_id: UUID,
    _: dict = Depends(require_superuser),
    db: Session = Depends(get_db),
) -> None:
    action = db.get(QuickAction, action_id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="quick action not found")
    db.delete(action)
    db.commit()


@router.get("/flags", response_model=List[FeatureFlagOut])
def get_feature_flags(_: dict = Depends(require_any_user), db: Session = Depends(get_db)) -> List[FeatureFlagOut]:
    return db.query(FeatureFlag).order_by(FeatureFlag.key.asc()).all()


@router.put("/flags/{flag_key}", response_model=FeatureFlagOut)
def upsert_flag(
    flag_key: str,
    body: FeatureFlagUpdate,
    _: dict = Depends(require_superuser),
    db: Session = Depends(get_db),
) -> FeatureFlagOut:
    flag = db.get(FeatureFlag, flag_key)
    if not flag:
        flag = FeatureFlag(key=flag_key)
        db.add(flag)
        db.flush()
    if body.description is not None:
        flag.description = body.description
    if body.value is not None:
        flag.value = body.value
    db.commit()
    db.refresh(flag)
    return flag
