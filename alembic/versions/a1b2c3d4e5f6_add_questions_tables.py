"""add questions tables

Revision ID: a1b2c3d4e5f6
Revises: ef1a2b3c4d56
Create Date: 2025-11-29 19:15:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "a1b2c3d4e5f6"
down_revision = "ef1a2b3c4d56"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False, server_default="open"),
        sa.Column("options", postgresql.JSONB()),
        sa.Column("reward_credits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reward_coins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_questions_category", "questions", ["category"])

    op.create_table(
        "question_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("answer", postgresql.JSONB()),
        sa.Column("credits_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("coins_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_question_responses_question", "question_responses", ["question_id"])
    op.create_index("ix_question_responses_user", "question_responses", ["user_id"])

    op.create_table(
        "question_credits",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("question_credits")
    op.drop_index("ix_question_responses_user", table_name="question_responses")
    op.drop_index("ix_question_responses_question", table_name="question_responses")
    op.drop_table("question_responses")
    op.drop_index("ix_questions_category", table_name="questions")
    op.drop_table("questions")
