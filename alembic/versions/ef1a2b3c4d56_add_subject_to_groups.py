"""Add subject column to groups

Revision ID: ef1a2b3c4d56
Revises: d3c1f005b2e1
Create Date: 2025-11-04 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ef1a2b3c4d56"
down_revision: Union[str, Sequence[str], None] = "d3c1f005b2e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("groups", sa.Column("subject", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("groups", "subject")
