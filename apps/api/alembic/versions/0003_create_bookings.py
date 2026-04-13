"""create bookings table

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("schedule_id", sa.String(), nullable=False),
        sa.Column("slot_id", sa.String(), nullable=False),
        sa.Column("guest_name", sa.String(), nullable=False),
        sa.Column("guest_email", sa.String(), nullable=False),
        sa.Column("guest_note", sa.String(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "cancelled", name="booking_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("confirmation_token", sa.String(), nullable=False),
        sa.Column("cancel_token", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["slot_id"], ["slots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slot_id"),
        sa.UniqueConstraint("confirmation_token"),
        sa.UniqueConstraint("cancel_token"),
    )
    op.create_index("ix_bookings_schedule_id", "bookings", ["schedule_id"])
    op.create_index("ix_bookings_confirmation_token", "bookings", ["confirmation_token"])
    op.create_index("ix_bookings_cancel_token", "bookings", ["cancel_token"])


def downgrade() -> None:
    op.drop_index("ix_bookings_cancel_token", table_name="bookings")
    op.drop_index("ix_bookings_confirmation_token", table_name="bookings")
    op.drop_index("ix_bookings_schedule_id", table_name="bookings")
    op.drop_table("bookings")
    op.execute("DROP TYPE IF EXISTS booking_status")
