"""create schedules and slots tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "schedules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("buffer_before", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("buffer_after", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("availability", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("timezone", sa.String(), nullable=False, server_default="UTC"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("color", sa.String(), nullable=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schedules_user_id", "schedules", ["user_id"])

    op.create_table(
        "slots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("schedule_id", sa.String(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("available", "booked", "blocked", name="slot_status"),
            nullable=False,
            server_default="available",
        ),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_slots_schedule_id", "slots", ["schedule_id"])


def downgrade() -> None:
    op.drop_index("ix_slots_schedule_id", table_name="slots")
    op.drop_table("slots")
    op.drop_index("ix_schedules_user_id", table_name="schedules")
    op.drop_table("schedules")
    op.execute("DROP TYPE IF EXISTS slot_status")
