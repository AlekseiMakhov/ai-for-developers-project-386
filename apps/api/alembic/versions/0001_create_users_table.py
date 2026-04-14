"""create users table

Revision ID: 0001
Revises:
Create Date: 2026-04-13

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("timezone", sa.String(), nullable=False, server_default="UTC"),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_slug", "users", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_slug", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
