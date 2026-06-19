"""add user last_seen_at

Revision ID: b7f9d3a8e2c1
Revises: 5432344d40f8
Create Date: 2026-02-27 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7f9d3a8e2c1"
down_revision: str | Sequence[str] | None = "5432344d40f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("user", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_user_last_seen_at", "user", ["last_seen_at"], unique=False)
    op.execute('UPDATE "user" SET last_seen_at = creation_datetime WHERE last_seen_at IS NULL')


def downgrade() -> None:
    op.drop_index("ix_user_last_seen_at", table_name="user")
    op.drop_column("user", "last_seen_at")
