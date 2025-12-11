"""Set users.role default to professor

Revision ID: 4cf5def7be53
Revises: e0abc55cdff4
Create Date: 2025-11-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "4cf5def7be53"
down_revision: Union[str, Sequence[str], None] = "e0abc55cdff4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


role_enum = sa.Enum("student", "professor", "superuser", name="role")


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "role",
        existing_type=role_enum,
        server_default=sa.text("'professor'"),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "role",
        existing_type=role_enum,
        server_default=sa.text("'student'"),
        existing_nullable=False,
    )
