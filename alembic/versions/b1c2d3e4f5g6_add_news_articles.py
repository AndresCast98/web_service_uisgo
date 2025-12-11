"""add news articles

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2025-11-29 19:25:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b1c2d3e4f5g6"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subtitle", sa.String(length=255)),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("tag", sa.String(length=32)),
        sa.Column("image_url", sa.String(length=512)),
        sa.Column("cta_url", sa.String(length=512)),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("publish_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_news_articles_category", "news_articles", ["category"])
    op.create_index("ix_news_articles_published", "news_articles", ["published"])


def downgrade() -> None:
    op.drop_index("ix_news_articles_published", table_name="news_articles")
    op.drop_index("ix_news_articles_category", table_name="news_articles")
    op.drop_table("news_articles")
