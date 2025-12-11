"""add places tables

Revision ID: d1e2f3g4h5i6
Revises: c1d2e3f4g5h6
Create Date: 2025-11-29 19:45:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d1e2f3g4h5i6"
down_revision = "c1d2e3f4g5h6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "places",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("thumbnail_url", sa.String(length=512)),
        sa.Column("location", postgresql.JSONB()),
        sa.Column("contact", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_places_category", "places", ["category"])

    op.create_table(
        "place_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("places.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("price", sa.Numeric(scale=2)),
        sa.Column("image_url", sa.String(length=512)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_place_products_place", "place_products", ["place_id"])


def downgrade() -> None:
    op.drop_index("ix_place_products_place", table_name="place_products")
    op.drop_table("place_products")
    op.drop_index("ix_places_category", table_name="places")
    op.drop_table("places")
