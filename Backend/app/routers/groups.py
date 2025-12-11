import io
import secrets
import string
from datetime import datetime
from typing import List
from uuid import UUID

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, require_role, require_student
from app.models.activity import ActivityTarget
from app.models.group import Group, GroupMembership
from app.models.invite import InviteCode
from app.models.question import Question, QuestionTarget
from app.models.user import User
from app.schemas.group import (
    GroupCreate,
    GroupDetail,
    GroupOut,
    GroupUpdate,
    InviteCreate,
    JoinByCode,
    GroupQuestionSummary,
)

router = APIRouter()
require_prof_or_super = require_role("professor", "superuser")
require_any_user = require_role("student", "professor", "superuser", "communications")


def _code(n: int = 8) -> str:
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(n))


DEEP_LINK_PREFIX = settings.DEEP_LINK_PREFIX
WEB_BASE_URL = settings.ADMIN_WEB_BASE_URL  # ajustar en despliegue


def _student_count(value: int | None) -> int:
    return max((value or 0) - 1, 0)


def _group_summary(
    group: Group,
    owner: User,
    member_count: int,
) -> GroupOut:
    return GroupOut(
        id=group.id,
        name=group.name,
        subject=group.subject,
        created_at=group.created_at,
        student_count=_student_count(member_count),
        owner_email=owner.email,
        owner_name=owner.full_name,
    )


def _group_detail(
    group: Group,
    owner: User,
    member_count: int,
    invite: InviteCode | None,
    questions: list[GroupQuestionSummary] | None = None,
) -> GroupDetail:
    detail = GroupDetail(
        id=group.id,
        name=group.name,
        subject=group.subject,
        created_at=group.created_at,
        student_count=_student_count(member_count),
        owner_email=owner.email,
        owner_name=owner.full_name,
    )
    if invite:
        detail.invite_code = invite.code
        detail.web_join = f"{WEB_BASE_URL}/join?code={invite.code}"
        detail.deep_link = f"{DEEP_LINK_PREFIX}{invite.code}"
        detail.qr_png = f"{WEB_BASE_URL}/groups/{group.id}/invites/{invite.code}/qr.png"
    detail.questions = questions or []
    return detail


def _group_questions(db: Session, group_id: UUID) -> list[GroupQuestionSummary]:
    rows = (
        db.query(Question)
        .join(QuestionTarget, QuestionTarget.question_id == Question.id)
        .filter(QuestionTarget.group_id == group_id)
        .order_by(Question.created_at.desc())
        .all()
    )
    return [
        GroupQuestionSummary(
            id=row.id,
            title=row.title,
            category=row.category,
            reward_credits=row.reward_credits or 0,
        )
        for row in rows
    ]


def _get_group_with_owner(db: Session, group_id: UUID) -> tuple[Group, User]:
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="group not found")
    owner = db.get(User, group.created_by)
    if not owner:
        raise HTTPException(status_code=400, detail="group owner missing")
    return group, owner


def _ensure_permissions(group: Group, user_payload: dict) -> None:
    if user_payload.get("role") == "professor" and str(group.created_by) != user_payload.get("sub"):
        raise HTTPException(status_code=403, detail="forbidden")


def _latest_active_invite(db: Session, group_id: UUID) -> InviteCode | None:
    return (
        db.query(InviteCode)
        .filter(InviteCode.group_id == group_id, InviteCode.is_active.is_(True))
        .order_by(InviteCode.created_at.desc())
        .first()
    )


@router.get("/", response_model=List[GroupOut])
def list_groups(
    search: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_prof_or_super),
) -> List[GroupOut]:
    query = (
        db.query(
            Group,
            User,
            func.count(GroupMembership.id).label("member_count"),
        )
        .join(User, Group.created_by == User.id)
        .outerjoin(GroupMembership, GroupMembership.group_id == Group.id)
        .group_by(Group.id, User.id)
        .order_by(Group.created_at.desc())
    )
    if user["role"] == "professor":
        query = query.filter(Group.created_by == user["sub"])
    if search:
        like = f"%{search.strip().lower()}%"
        query = query.filter(func.lower(Group.name).like(like))
    rows = query.all()
    return [_group_summary(group, owner, member_count) for group, owner, member_count in rows]


@router.post("/", response_model=GroupDetail, status_code=status.HTTP_201_CREATED)
def create_group(
    body: GroupCreate,
    db: Session = Depends(get_db),
    user=Depends(require_prof_or_super),
) -> GroupDetail:
    group = Group(name=body.name, subject=body.subject, created_by=user["sub"])
    db.add(group)
    db.commit()
    db.refresh(group)

    db.add(GroupMembership(group_id=group.id, user_id=user["sub"], role_in_group="owner"))
    db.commit()

    code = _code(8)
    invite = InviteCode(group_id=group.id, code=code, created_by=user["sub"])
    db.add(invite)
    db.commit()
    db.refresh(invite)

    owner = db.get(User, user["sub"])
    if not owner:
        raise HTTPException(status_code=400, detail="owner not found")
    return _group_detail(group, owner, member_count=1, invite=invite, questions=[])


@router.post("/{group_id}/invites")
def create_invite(
    group_id: UUID,
    body: InviteCreate,
    db: Session = Depends(get_db),
    user=Depends(require_prof_or_super),
):
    group, _ = _get_group_with_owner(db, group_id)
    _ensure_permissions(group, user)
    code = _code(8)
    invite = InviteCode(
        group_id=group_id,
        code=code,
        expires_at=body.expires_at,
        max_uses=body.max_uses,
        created_by=user["sub"],
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return {"code": invite.code}


@router.post("/join", dependencies=[Depends(require_student)])
def join_group(body: JoinByCode, user=Depends(require_student), db: Session = Depends(get_db)):
    invite = (
        db.query(InviteCode)
        .filter(InviteCode.code == body.code, InviteCode.is_active.is_(True))
        .first()
    )
    if not invite:
        raise HTTPException(status_code=400, detail="invalid code")
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="expired code")
    if invite.max_uses and invite.uses >= invite.max_uses:
        raise HTTPException(status_code=400, detail="max uses reached")

    exists = (
        db.query(GroupMembership)
        .filter(
            GroupMembership.group_id == invite.group_id,
            GroupMembership.user_id == user["sub"],
        )
        .first()
    )
    if not exists:
        db.add(GroupMembership(group_id=invite.group_id, user_id=user["sub"]))
        invite.uses += 1
        db.commit()
    return {"joined": True}


@router.get("/me", response_model=List[GroupOut])
def list_my_groups(user=Depends(require_any_user), db: Session = Depends(get_db)) -> List[GroupOut]:
    query = (
        db.query(
            Group,
            User,
            func.count(GroupMembership.id).label("member_count"),
        )
        .join(User, Group.created_by == User.id)
        .join(GroupMembership, GroupMembership.group_id == Group.id)
    )
    if user["role"] == "student":
        query = query.filter(GroupMembership.user_id == user["sub"])
    else:
        query = query.filter(Group.created_by == user["sub"])
    query = query.group_by(Group.id, User.id).order_by(Group.created_at.desc())
    rows = query.all()
    return [_group_summary(group, owner, member_count) for group, owner, member_count in rows]


@router.get("/{group_id}", response_model=GroupDetail)
def get_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(require_prof_or_super),
) -> GroupDetail:
    group, owner = _get_group_with_owner(db, group_id)
    _ensure_permissions(group, user)
    member_count = (
        db.query(func.count(GroupMembership.id))
        .filter(GroupMembership.group_id == group.id)
        .scalar()
    )
    invite = _latest_active_invite(db, group_id)
    questions = _group_questions(db, group.id)
    return _group_detail(group, owner, member_count=member_count or 0, invite=invite, questions=questions)


@router.put("/{group_id}", response_model=GroupDetail)
def update_group(
    group_id: UUID,
    body: GroupUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_prof_or_super),
) -> GroupDetail:
    group, owner = _get_group_with_owner(db, group_id)
    _ensure_permissions(group, user)
    if body.name is not None:
        group.name = body.name
    if body.subject is not None:
        group.subject = body.subject
    db.commit()
    db.refresh(group)
    member_count = (
        db.query(func.count(GroupMembership.id))
        .filter(GroupMembership.group_id == group.id)
        .scalar()
    )
    invite = _latest_active_invite(db, group_id)
    questions = _group_questions(db, group.id)
    return _group_detail(group, owner, member_count=member_count or 0, invite=invite, questions=questions)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(require_prof_or_super),
) -> Response:
    group, _ = _get_group_with_owner(db, group_id)
    _ensure_permissions(group, user)

    db.query(GroupMembership).filter(GroupMembership.group_id == group.id).delete(synchronize_session=False)
    db.query(ActivityTarget).filter(ActivityTarget.group_id == group.id).delete(synchronize_session=False)
    db.query(InviteCode).filter(InviteCode.group_id == group.id).delete(synchronize_session=False)
    db.delete(group)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{group_id}/invites/{code}/qr.png")
def invite_qr_png(
    group_id: UUID,
    code: str,
    db: Session = Depends(get_db),
    user=Depends(require_prof_or_super),
):
    group, _ = _get_group_with_owner(db, group_id)
    _ensure_permissions(group, user)
    invite = (
        db.query(InviteCode)
        .filter(
            InviteCode.group_id == group_id,
            InviteCode.code == code,
            InviteCode.is_active.is_(True),
        )
        .first()
    )
    if not invite:
        raise HTTPException(status_code=404, detail="invalid invite")

    target = f"{WEB_BASE_URL}/join?code={code}"
    img = qrcode.make(target)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
