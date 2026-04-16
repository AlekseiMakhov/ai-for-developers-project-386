"""remove buffer_before and buffer_after columns from schedules

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("schedules", "buffer_before")
    op.drop_column("schedules", "buffer_after")


def downgrade() -> None:
    op.add_column("schedules", sa.Column("buffer_after", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("schedules", sa.Column("buffer_before", sa.Integer(), nullable=False, server_default="0"))
