from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.coins import CoinsLedger
from app.models.group import Group, GroupMembership
from app.models.question import Question, QuestionCredit, QuestionResponse, QuestionTarget
from app.models.user import User
from app.schemas.questions import (
    QuestionAnswerIn,
    QuestionAnswerOut,
    QuestionCreate,
    QuestionCreditsOut,
    QuestionGroupOut,
    QuestionOut,
    QuestionResponseItem,
    QuestionTargetsUpdate,
)

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications")
require_prof_or_super = require_role("professor", "superuser")


def _ensure_professor_access(question: Question, user: dict) -> None:
    if user["role"] == "professor" and str(question.created_by) != user["sub"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")


def _validate_group_ids(db: Session, group_ids: List[UUID], user: dict) -> List[UUID]:
    if not group_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="group_ids required")
    unique_ids = list(dict.fromkeys(group_ids))
    groups = db.query(Group).filter(Group.id.in_(unique_ids)).all()
    if len(groups) != len(unique_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid group id")
    if user["role"] == "professor":
        for group in groups:
            if str(group.created_by) != user["sub"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return unique_ids


def _replace_question_targets(db: Session, question_id: UUID, group_ids: List[UUID]) -> None:
    db.query(QuestionTarget).filter(QuestionTarget.question_id == question_id).delete(synchronize_session=False)
    for gid in group_ids:
        db.add(QuestionTarget(question_id=question_id, group_id=gid))


def _question_groups_map(db: Session, question_ids: List[UUID]) -> Dict[UUID, List[QuestionGroupOut]]:
    mapping: Dict[UUID, List[QuestionGroupOut]] = defaultdict(list)
    if not question_ids:
        return mapping
    rows = (
        db.query(QuestionTarget.question_id, Group.id, Group.name)
        .join(Group, Group.id == QuestionTarget.group_id)
        .filter(QuestionTarget.question_id.in_(question_ids))
        .all()
    )
    for question_id, group_id, group_name in rows:
        mapping[question_id].append(QuestionGroupOut(id=group_id, name=group_name))
    return mapping


def _serialize_questions(db: Session, questions: List[Question]) -> List[QuestionOut]:
    mapping = _question_groups_map(db, [q.id for q in questions])
    result: List[QuestionOut] = []
    for question in questions:
        payload = QuestionOut.from_orm(question)
        groups = mapping.get(question.id, [])
        payload.groups = groups
        payload.is_global = len(groups) == 0
        result.append(payload)
    return result


@router.get("/credits", response_model=QuestionCreditsOut)
def get_credits(user=Depends(require_any_user), db: Session = Depends(get_db)) -> QuestionCreditsOut:
    record = db.get(QuestionCredit, user["sub"])
    if not record:
        record = QuestionCredit(user_id=user["sub"], balance=0, updated_at=datetime.utcnow())
        db.add(record)
        db.commit()
        db.refresh(record)
    return QuestionCreditsOut(balance=record.balance, last_updated=record.updated_at or datetime.utcnow())


@router.get("/", response_model=List[QuestionOut])
def list_questions(
    category: Optional[str] = None,
    group_id: Optional[UUID] = None,
    only_global: bool = False,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> List[QuestionOut]:
    query = db.query(Question).filter(Question.active.is_(True)).order_by(Question.created_at.desc())
    if category:
        query = query.filter(Question.category == category)

    if user["role"] == "professor":
        query = query.filter(Question.created_by == user["sub"])

    if only_global:
        query = (
            query.outerjoin(QuestionTarget, QuestionTarget.question_id == Question.id)
            .filter(QuestionTarget.group_id.is_(None))
        )
    elif group_id:
        group = db.get(Group, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="group not found")
        if user["role"] == "professor" and str(group.created_by) != user["sub"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        query = (
            query.join(QuestionTarget, QuestionTarget.question_id == Question.id)
            .filter(QuestionTarget.group_id == group_id)
        )
    elif user["role"] == "student":
        member_query = db.query(GroupMembership.group_id).filter(GroupMembership.user_id == user["sub"])
        query = (
            query.join(QuestionTarget, QuestionTarget.question_id == Question.id)
            .filter(QuestionTarget.group_id.in_(member_query))
        )
    rows = query.distinct().offset(offset).limit(limit).all()
    return _serialize_questions(db, rows)


def _serialize_responses(
    db: Session, rows: List[tuple[QuestionResponse, Question, User]]
) -> List[QuestionResponseItem]:
    mapping = _question_groups_map(db, [question.id for _, question, _ in rows])
    result: List[QuestionResponseItem] = []
    for response, question, student in rows:
        groups = mapping.get(question.id, [])
        result.append(
            QuestionResponseItem(
                id=response.id,
                question_id=question.id,
                question_title=question.title,
                student_email=student.email,
                student_name=student.full_name,
                answer=response.answer,
                credits_awarded=response.credits_awarded,
                coins_awarded=response.coins_awarded,
                created_at=response.created_at,
                groups=groups,
                is_global=len(groups) == 0,
            )
        )
    return result


@router.get("/responses", response_model=List[QuestionResponseItem])
def list_question_responses(
    group_id: Optional[UUID] = None,
    question_id: Optional[UUID] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user=Depends(require_prof_or_super),
    db: Session = Depends(get_db),
) -> List[QuestionResponseItem]:
    query = (
        db.query(QuestionResponse, Question, User)
        .join(Question, Question.id == QuestionResponse.question_id)
        .join(User, User.id == QuestionResponse.user_id)
    )
    if user["role"] == "professor":
        query = query.filter(Question.created_by == user["sub"])
    if question_id:
        query = query.filter(QuestionResponse.question_id == question_id)
    if group_id:
        query = (
            query.join(QuestionTarget, QuestionTarget.question_id == Question.id)
            .filter(QuestionTarget.group_id == group_id)
        )
    rows = (
        query.order_by(QuestionResponse.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return _serialize_responses(db, rows)


@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(
    body: QuestionCreate,
    user=Depends(require_prof_or_super),
    db: Session = Depends(get_db),
) -> QuestionOut:
    group_ids = _validate_group_ids(db, body.group_ids or [], user)
    question = Question(
        title=body.title,
        body=body.body,
        category=body.category,
        type=body.type,
        options=body.options,
        reward_credits=body.reward_credits,
        reward_coins=body.reward_coins,
        created_by=user["sub"],
    )
    db.add(question)
    db.flush()
    if group_ids:
        _replace_question_targets(db, question.id, group_ids)
    db.commit()
    db.refresh(question)
    return _serialize_questions(db, [question])[0]


@router.put("/{question_id}/targets", response_model=QuestionOut)
def update_question_targets(
    question_id: UUID,
    body: QuestionTargetsUpdate,
    user=Depends(require_prof_or_super),
    db: Session = Depends(get_db),
) -> QuestionOut:
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="question not found")
    _ensure_professor_access(question, user)
    group_ids = _validate_group_ids(db, body.group_ids, user)
    _replace_question_targets(db, question_id, group_ids)
    db.commit()
    db.refresh(question)
    return _serialize_questions(db, [question])[0]


@router.post("/{question_id}/answer", response_model=QuestionAnswerOut)
def answer_question(
    question_id: UUID,
    body: QuestionAnswerIn,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> QuestionAnswerOut:
    question = db.get(Question, question_id)
    if not question or not question.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="question not available")

    exists = (
        db.query(QuestionResponse)
        .filter(QuestionResponse.question_id == question_id, QuestionResponse.user_id == user["sub"])
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="question already answered")

    credits = db.get(QuestionCredit, user["sub"])
    if not credits:
        credits = QuestionCredit(user_id=user["sub"], balance=0)
        db.add(credits)
        db.flush()

    credits_awarded = question.reward_credits or 0
    coins_awarded = question.reward_coins or 0
    credits.balance = credits.balance + credits_awarded
    credits.updated_at = datetime.utcnow()

    response = QuestionResponse(
        question_id=question_id,
        user_id=user["sub"],
        answer=body.answer,
        credits_awarded=credits_awarded,
        coins_awarded=coins_awarded,
    )
    db.add(response)

    if coins_awarded > 0:
        ledger_entry = CoinsLedger(
            user_id=user["sub"],
            delta=coins_awarded,
            reason="Question reward",
            activity_id=None,
        )
        db.add(ledger_entry)

    db.commit()

    return QuestionAnswerOut(
        question_id=question_id,
        credits_awarded=credits_awarded,
        coins_awarded=coins_awarded,
        new_credit_balance=credits.balance,
    )
