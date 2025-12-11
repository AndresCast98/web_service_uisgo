from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.wellness import WellnessPrompt, UserMood, WellnessCenter, WellnessTurn
from app.schemas.wellness import (
    CreateTurnIn,
    RecordMoodIn,
    UserMoodOut,
    WellnessCenterCreate,
    WellnessCenterOut,
    WellnessPromptCreate,
    WellnessPromptOut,
    WellnessTurnOut,
)

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications")
require_superuser = require_role("superuser")


@router.get("/prompts", response_model=List[WellnessPromptOut])
def list_prompts(
    screen: str,
    db: Session = Depends(get_db),
) -> List[WellnessPromptOut]:
    return (
        db.query(WellnessPrompt)
        .filter(WellnessPrompt.screen == screen, WellnessPrompt.active.is_(True))
        .order_by(WellnessPrompt.created_at.desc())
        .all()
    )


@router.post("/prompts", response_model=WellnessPromptOut, status_code=status.HTTP_201_CREATED)
def create_prompt(
    body: WellnessPromptCreate,
    _: dict = Depends(require_superuser),
    db: Session = Depends(get_db),
) -> WellnessPromptOut:
    prompt = WellnessPrompt(**body.model_dump())
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@router.post("/moods", response_model=UserMoodOut, status_code=status.HTTP_201_CREATED)
def record_mood(
    body: RecordMoodIn,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> UserMoodOut:
    prompt = db.get(WellnessPrompt, body.prompt_id)
    if not prompt or not prompt.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="prompt not available")

    mood = UserMood(
        user_id=user["sub"],
        prompt_id=body.prompt_id,
        mood_value=body.mood_value,
        metadata=body.metadata,
    )
    db.add(mood)
    db.commit()
    db.refresh(mood)
    return mood


@router.get("/centers", response_model=List[WellnessCenterOut])
def list_centers(db: Session = Depends(get_db)) -> List[WellnessCenterOut]:
    return db.query(WellnessCenter).order_by(WellnessCenter.created_at.asc()).all()


@router.post("/centers", response_model=WellnessCenterOut, status_code=status.HTTP_201_CREATED)
def create_center(
    body: WellnessCenterCreate,
    _: dict = Depends(require_superuser),
    db: Session = Depends(get_db),
) -> WellnessCenterOut:
    center = WellnessCenter(**body.model_dump())
    db.add(center)
    db.commit()
    db.refresh(center)
    return center


@router.post("/turns", response_model=WellnessTurnOut, status_code=status.HTTP_201_CREATED)
def create_turn(
    body: CreateTurnIn,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> WellnessTurnOut:
    center = db.get(WellnessCenter, body.center_id)
    if not center:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="center not found")

    turn = WellnessTurn(
        center_id=body.center_id,
        user_id=user["sub"],
        scheduled_at=body.scheduled_at,
        status="waiting",
        qr_token=None,
    )
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn


@router.get("/turns/me", response_model=List[WellnessTurnOut])
def my_turns(
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> List[WellnessTurnOut]:
    return (
        db.query(WellnessTurn)
        .filter(WellnessTurn.user_id == user["sub"])
        .order_by(WellnessTurn.scheduled_at.desc())
        .limit(limit)
        .all()
    )
