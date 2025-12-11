from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_professor, require_student, require_role
from app.models.activity import Activity, ActivityTarget, ActivityStatus, ActivityType
from app.models.coins import CoinsLedger
from app.models.group import Group, GroupMembership
from app.models.submission import Submission, SubmissionStatus
from app.models.user import User
from app.schemas.activity import (
    ActivityCreate,
    ActivityDetailOut,
    ActivityOut,
    ActivitySubmissionOut,
    ActivityTargetOut,
    AnswerIn,
)

router = APIRouter()

require_prof_or_super = require_role("professor", "superuser")
require_any_user = require_role("student", "professor", "superuser", "communications")


def _as_utc(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _ensure_group_access(db: Session, group_id: UUID, user_payload: dict) -> Group:
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="group not found")
    if user_payload.get("role") == "professor" and str(group.created_by) != user_payload.get("sub"):
        raise HTTPException(status_code=403, detail="forbidden")
    return group


def _ensure_activity_access(db: Session, activity: Activity, user_payload: dict) -> None:
    role = user_payload.get("role")
    if role == "superuser":
        return
    if str(activity.created_by) == user_payload.get("sub"):
        return
    owns_group = (
        db.query(ActivityTarget)
        .join(Group, Group.id == ActivityTarget.group_id)
        .filter(
            ActivityTarget.activity_id == activity.id,
            Group.created_by == user_payload.get("sub"),
        )
        .first()
    )
    if owns_group:
        return
    raise HTTPException(status_code=403, detail="forbidden")

@router.post("/")
def create_activity(body: ActivityCreate, user=Depends(require_prof_or_super), db: Session = Depends(get_db)):
    for gid in body.target_group_ids:
        _ensure_group_access(db, gid, user)

    a = Activity(
        title=body.title, description=body.description,
        type=ActivityType(body.type),
        q_text=body.q_text, q_type=body.q_type,
        q_options=body.q_options, q_correct=body.q_correct,
        coins_on_complete=body.coins_on_complete,
        start_at=body.start_at, end_at=body.end_at,
        created_by=user["sub"]
    )
    db.add(a); db.commit(); db.refresh(a)
    for gid in body.target_group_ids:
        db.add(ActivityTarget(activity_id=a.id, group_id=gid))
    db.commit()
    return {"id": str(a.id)}


@router.get("/group/{group_id}", response_model=List[ActivityOut])
def list_group_activities(group_id: UUID, user=Depends(require_prof_or_super), db: Session = Depends(get_db)):
    _ensure_group_access(db, group_id, user)
    rows = (
        db.query(Activity)
        .join(ActivityTarget, ActivityTarget.activity_id == Activity.id)
        .filter(ActivityTarget.group_id == group_id)
        .order_by(Activity.created_at.desc())
        .all()
    )
    return [
        ActivityOut(
            id=a.id,
            title=a.title,
            description=a.description,
            type=a.type.value,
            status=a.status.value,
            coins_on_complete=a.coins_on_complete,
            start_at=a.start_at,
            end_at=a.end_at,
            created_at=a.created_at,
        )
        for a in rows
    ]

@router.get("/{activity_id}", response_model=ActivityDetailOut)
def get_activity_detail(activity_id: UUID, user=Depends(require_prof_or_super), db: Session = Depends(get_db)):
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="activity not found")
    _ensure_activity_access(db, activity, user)

    target_rows = (
        db.query(ActivityTarget, Group)
        .join(Group, Group.id == ActivityTarget.group_id)
        .filter(ActivityTarget.activity_id == activity.id)
        .all()
    )
    target_out = [ActivityTargetOut(id=g.id, name=g.name) for _, g in target_rows]

    submission_rows = (
        db.query(Submission, User)
        .join(User, User.id == Submission.user_id)
        .filter(Submission.activity_id == activity.id)
        .order_by(Submission.created_at.desc())
        .all()
    )

    submissions_out = [
        ActivitySubmissionOut(
            id=sub.id,
            student_id=student.id,
            student_name=student.full_name,
            student_email=student.email,
            status=sub.status.value,
            is_correct=sub.is_correct,
            awarded_coins=sub.awarded_coins,
            answer=sub.answer,
            submitted_at=sub.created_at,
        )
        for sub, student in submission_rows
    ]

    return ActivityDetailOut(
        id=activity.id,
        title=activity.title,
        description=activity.description,
        type=activity.type.value,
        status=activity.status.value,
        coins_on_complete=activity.coins_on_complete,
        start_at=activity.start_at,
        end_at=activity.end_at,
        created_at=activity.created_at,
        q_text=activity.q_text,
        q_options=activity.q_options,
        q_correct=activity.q_correct,
        target_groups=target_out,
        submissions=submissions_out,
    )


@router.post("/{activity_id}/publish", dependencies=[Depends(require_professor)])
def publish_activity(activity_id: str, db: Session = Depends(get_db)):
    a = db.get(Activity, activity_id)
    if not a: raise HTTPException(status_code=404, detail="not found")
    a.status = ActivityStatus.published
    db.commit()
    return {"published": True}

@router.get("/visible")
def my_visible_activities(user=Depends(require_any_user), db: Session = Depends(get_db)):
    sql = """
    select distinct a.*
    from activities a
    join activity_targets t on t.activity_id = a.id
    join group_membership gm on gm.group_id = t.group_id
    where gm.user_id = :uid
      and a.status = 'published'
      and (a.start_at is null or a.start_at <= now())
      and (a.end_at   is null or a.end_at   >= now())
    order by a.start_at nulls first, a.created_at desc
    """
    rows = db.execute(text(sql), {"uid": user["sub"]}).mappings().all()
    return [dict(r) for r in rows]

def _auto_grade(a: Activity, ans: AnswerIn):
    if a.type != ActivityType.quiz_single: return None, 0
    selected = (ans.selected or [])
    correct = (a.q_correct or [])
    is_correct = (selected == correct)
    awarded = a.coins_on_complete if is_correct else 0
    return is_correct, awarded

@router.post("/{activity_id}/submissions")
def submit(activity_id: str, body: AnswerIn, user=Depends(require_any_user), db: Session = Depends(get_db)):
    a = db.get(Activity, activity_id)
    if not a: raise HTTPException(status_code=404, detail="activity not found")
    if a.status != ActivityStatus.published:
        raise HTTPException(status_code=400, detail="not published")

    now = datetime.now(timezone.utc)
    start = _as_utc(a.start_at)
    end   = _as_utc(a.end_at)

    if start and now < start: raise HTTPException(status_code=400, detail="not started")
    if end   and now > end:   raise HTTPException(status_code=400, detail="ended")

    sql = text("""
    select 1
    from activity_targets t
    join group_membership gm on gm.group_id = t.group_id
    where t.activity_id = :aid and gm.user_id = :uid
    limit 1
    """)
    ok = db.execute(sql, {"aid": str(a.id), "uid": str(user["sub"])}).first()
    if not ok: raise HTTPException(status_code=403, detail="not allowed")

    dup = db.query(Submission).filter(Submission.activity_id == a.id, Submission.user_id == user["sub"]).first()
    if dup: raise HTTPException(status_code=400, detail="already submitted")

    sub = Submission(activity_id=a.id, user_id=user["sub"], answer=body.model_dump())
    if a.type == ActivityType.quiz_single:
        is_correct, awarded = _auto_grade(a, body)
        sub.is_correct = is_correct
        sub.status = SubmissionStatus.approved if is_correct else SubmissionStatus.submitted
        sub.awarded_coins = awarded
        db.add(sub); db.commit(); db.refresh(sub)
        if awarded > 0:
            db.add(CoinsLedger(user_id=user["sub"], activity_id=a.id, delta=awarded, reason="Activity completion (auto)"))
            db.commit()
    else:
        db.add(sub); db.commit(); db.refresh(sub)
    return {
        "submission_id": str(sub.id),
        "status": sub.status.value,
        "is_correct": sub.is_correct,
        "awarded_coins": sub.awarded_coins
    }
