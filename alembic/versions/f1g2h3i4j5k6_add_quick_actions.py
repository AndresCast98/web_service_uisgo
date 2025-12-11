"""add quick actions tables

Revision ID: f1g2h3i4j5k6
Revises: e1f2g3h4i5j6
Create Date: 2025-11-29 20:05:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f1g2h3i4j5k6"
down_revision = "e1f2g3h4i5j6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "quick_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("subtitle", sa.Text()),
        sa.Column("icon", sa.String(length=64)),
        sa.Column("target_route", sa.String(length=128), nullable=False),
        sa.Column("allowed_roles", sa.String(length=128), nullable=False, server_default="student,professor,superuser"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "feature_flags",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("description", sa.Text()),
        sa.Column("value", postgresql.JSONB()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("feature_flags")
    op.drop_table("quick_actions")
