"""add marketplace maps module

Revision ID: g3h4i5j6k7l8
Revises: f1g2h3i4j5k6
Create Date: 2025-11-30 23:15:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "g3h4i5j6k7l8"
down_revision = "f1g2h3i4j5k6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE role ADD VALUE IF NOT EXISTS 'market_manager'")

    op.add_column("places", sa.Column("kind", sa.String(length=32), nullable=False, server_default="store"))
    op.add_column("places", sa.Column("hero_image_url", sa.String(length=512)))
    op.add_column("places", sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb")))
    op.add_column("places", sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()))
    op.add_column("places", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()))
    op.add_column("places", sa.Column("status", sa.String(length=32), nullable=False, server_default="active"))

    op.add_column(
        "place_products",
        sa.Column("cta_url", sa.String(length=512)),
    )
    op.add_column(
        "place_products",
        sa.Column("order_index", sa.Numeric(precision=10, scale=2), server_default="0"),
    )

    op.create_table(
        "map_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("places.id")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subtitle", sa.String(length=255)),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column("location", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("contact", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("banner_url", sa.String(length=512)),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("visibility", sa.String(length=32), nullable=False, server_default="public"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_map_events_category", "map_events", ["category"])
    op.create_index("ix_map_events_visibility", "map_events", ["visibility"])
    op.create_index("ix_map_events_place_id", "map_events", ["place_id"])

    op.alter_column("places", "kind", server_default=None)
    op.alter_column("places", "status", server_default=None)
    op.alter_column("places", "tags", server_default=None)
    op.alter_column("places", "is_public", server_default=None)
    op.alter_column("places", "is_verified", server_default=None)
    op.alter_column("place_products", "order_index", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_map_events_place_id", table_name="map_events")
    op.drop_index("ix_map_events_visibility", table_name="map_events")
    op.drop_index("ix_map_events_category", table_name="map_events")
    op.drop_table("map_events")

    op.drop_column("place_products", "order_index")
    op.drop_column("place_products", "cta_url")

    op.drop_column("places", "status")
    op.drop_column("places", "is_verified")
    op.drop_column("places", "is_public")
    op.drop_column("places", "tags")
    op.drop_column("places", "hero_image_url")
    op.drop_column("places", "kind")


