"""add donation

Revision ID: c3e1a9f4b2d7
Revises: b7f9d3a8e2c1
Create Date: 2026-11-06 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3e1a9f4b2d7"
down_revision: str | Sequence[str] | None = "b7f9d3a8e2c1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "donation",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.Text(), nullable=False),
        sa.Column("telegram_payment_charge_id", sa.Text(), nullable=False),
        sa.Column("creation_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_donation")),
        sa.UniqueConstraint("telegram_payment_charge_id", name=op.f("uq_donation_telegram_payment_charge_id")),
    )
    op.create_index("ix_donation_user_id", "donation", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_donation_user_id", table_name="donation")
    op.drop_table("donation")
