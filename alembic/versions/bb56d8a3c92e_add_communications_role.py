"""Add communications role to role enum

Revision ID: bb56d8a3c92e
Revises: aa34c5b66e0e
Create Date: 2025-11-30 22:12:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "bb56d8a3c92e"
down_revision: Union[str, Sequence[str], None] = "aa34c5b66e0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE role ADD VALUE IF NOT EXISTS 'communications'")


def downgrade() -> None:
    pass

