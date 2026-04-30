"""add google_id to users, make hashed_password nullable

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-30

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_id", sa.String(), nullable=True))
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)
    op.alter_column("users", "hashed_password", nullable=True)


def downgrade() -> None:
    op.alter_column("users", "hashed_password", nullable=False)
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "google_id")
