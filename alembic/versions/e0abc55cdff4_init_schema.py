"""init schema

Revision ID: e0abc55cdff4
Revises: 
Create Date: 2025-11-03 21:32:24.929229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'e0abc55cdff4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('student', 'professor', 'superuser', name='role'), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('activities',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('type', sa.Enum('quiz_single', 'open', name='activitytype'), nullable=False),
    sa.Column('q_text', sa.String(), nullable=False),
    sa.Column('q_type', sa.Enum('single', 'open', name='questiontype'), nullable=False),
    sa.Column('q_options', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('q_correct', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('coins_on_complete', sa.Integer(), nullable=True),
    sa.Column('start_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.Enum('draft', 'published', 'closed', name='activitystatus'), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('groups',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_by', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('activity_targets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('activity_id', sa.UUID(), nullable=False),
    sa.Column('group_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('activity_id', 'group_id', name='uq_activity_group')
    )
    op.create_table('coins_ledger',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('activity_id', sa.UUID(), nullable=True),
    sa.Column('delta', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('group_membership',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('group_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('role_in_group', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('group_id', 'user_id', name='uq_group_user')
    )
    op.create_table('invite_codes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('group_id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('max_uses', sa.Integer(), nullable=True),
    sa.Column('uses', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invite_codes_code'), 'invite_codes', ['code'], unique=True)
    op.create_table('submissions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('activity_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('answer', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('submitted', 'approved', 'rejected', name='submissionstatus'), nullable=True),
    sa.Column('awarded_coins', sa.Integer(), nullable=True),
    sa.Column('graded_by', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ),
    sa.ForeignKeyConstraint(['graded_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('activity_id', 'user_id', name='uq_submission')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('submissions')
    op.drop_index(op.f('ix_invite_codes_code'), table_name='invite_codes')
    op.drop_table('invite_codes')
    op.drop_table('group_membership')
    op.drop_table('coins_ledger')
    op.drop_table('activity_targets')
    op.drop_table('groups')
    op.drop_table('activities')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
