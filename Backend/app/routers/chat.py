from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.chats import ChatSession, ChatMessage
from app.models.coins import CoinsLedger
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageOut,
    ChatSessionCreate,
    ChatSessionOut,
)
from app.services.chat_policy import DEFAULT_POLICY
from app.services.chat_service import generate_ai_reply

router = APIRouter()
require_any_user = require_role("student", "professor", "superuser", "communications")
COINS_PER_RESPONSE = 2


def _ensure_session(session: ChatSession | None, user_payload: dict) -> ChatSession:
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    if user_payload.get("role") != "superuser" and str(session.user_id) != user_payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return session


def _current_balance(db: Session, user_id: UUID) -> int:
    total = (
        db.query(func.coalesce(func.sum(CoinsLedger.delta), 0))
        .filter(CoinsLedger.user_id == user_id)
        .scalar()
    )
    return total or 0


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    body: ChatSessionCreate,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> ChatSessionOut:
    session = ChatSession(
        user_id=user["sub"],
        title=body.title,
        policy_version=DEFAULT_POLICY.version,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[ChatSessionOut])
def list_sessions(user=Depends(require_any_user), db: Session = Depends(get_db)) -> List[ChatSessionOut]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user["sub"])
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageOut])
def list_messages(
    session_id: UUID,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> List[ChatMessageOut]:
    session = _ensure_session(db.get(ChatSession, session_id), user)
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageOut)
def send_message(
    session_id: UUID,
    body: ChatMessageCreate,
    user=Depends(require_any_user),
    db: Session = Depends(get_db),
) -> ChatMessageOut:
    session = _ensure_session(db.get(ChatSession, session_id), user)

    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=body.content,
        attachments=body.attachments,
    )
    db.add(user_message)
    db.flush()

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    formatted_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]

    balance = _current_balance(db, session.user_id)
    if balance < COINS_PER_RESPONSE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="insufficient coins")

    reply = generate_ai_reply(formatted_history)

    assist_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=reply,
        coins_delta=-COINS_PER_RESPONSE,
    )
    db.add(assist_message)
    db.add(
        CoinsLedger(
            user_id=session.user_id,
            delta=-COINS_PER_RESPONSE,
            reason="Chat IA",
        )
    )
    session.coins_spent += COINS_PER_RESPONSE
    db.commit()
    db.refresh(assist_message)
    return assist_message
