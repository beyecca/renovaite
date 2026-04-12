"""add_updated_at_is_deleted_to_users

Revision ID: 071da0890d76
Revises: 86bd6a18206e
Create Date: 2026-04-11 19:15:48.366596

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '071da0890d76'
down_revision: Union[str, Sequence[str], None] = '86bd6a18206e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_magic_link_tokens_email'), 'magic_link_tokens', ['email'], unique=False)
    op.create_index(op.f('ix_magic_link_tokens_token'), 'magic_link_tokens', ['token'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_magic_link_tokens_token'), table_name='magic_link_tokens')
    op.drop_index(op.f('ix_magic_link_tokens_email'), table_name='magic_link_tokens')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
