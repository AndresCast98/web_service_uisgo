"""Add thumbnail and hero image urls to news articles

Revision ID: aa34c5b66e0e
Revises: ab12cd34ef56
Create Date: 2025-11-30 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "aa34c5b66e0e"
down_revision: Union[str, Sequence[str], None] = "ab12cd34ef56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("news_articles", sa.Column("thumbnail_url", sa.String(length=512), nullable=True))
    op.add_column("news_articles", sa.Column("hero_image_url", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("news_articles", "hero_image_url")
    op.drop_column("news_articles", "thumbnail_url")

