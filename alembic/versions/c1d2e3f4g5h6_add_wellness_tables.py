"""add wellness tables

Revision ID: c1d2e3f4g5h6
Revises: b1c2d3e4f5g6
Create Date: 2025-11-29 19:35:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "c1d2e3f4g5h6"
down_revision = "b1c2d3e4f5g6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wellness_prompts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("options", postgresql.JSONB(), nullable=False),
        sa.Column("screen", sa.String(length=64), nullable=False),
        sa.Column("frequency", sa.String(length=32), nullable=False, server_default="daily"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "user_moods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mood_value", sa.String(length=64), nullable=False),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_user_moods_user", "user_moods", ["user_id"])
    op.create_index("ix_user_moods_prompt", "user_moods", ["prompt_id"])

    op.create_table(
        "wellness_centers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("location", postgresql.JSONB()),
        sa.Column("contact", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "wellness_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("center_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="waiting"),
        sa.Column("qr_token", sa.String(length=128)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_wellness_turns_center", "wellness_turns", ["center_id"])
    op.create_index("ix_wellness_turns_user", "wellness_turns", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_wellness_turns_user", table_name="wellness_turns")
    op.drop_index("ix_wellness_turns_center", table_name="wellness_turns")
    op.drop_table("wellness_turns")
    op.drop_table("wellness_centers")
    op.drop_index("ix_user_moods_prompt", table_name="user_moods")
    op.drop_index("ix_user_moods_user", table_name="user_moods")
    op.drop_table("user_moods")
    op.drop_table("wellness_prompts")
