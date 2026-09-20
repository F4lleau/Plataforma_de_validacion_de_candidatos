"""complete task 02b affiliation validation

Revision ID: 8c4f2e91b6a7
Revises: 734865b8795b
Create Date: 2026-09-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c4f2e91b6a7"
down_revision: Union[str, Sequence[str], None] = "734865b8795b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "affiliate_import_batches",
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(
        "uq_affiliate_import_batches_current",
        "affiliate_import_batches",
        ["is_current"],
        unique=True,
        postgresql_where=sa.text("is_current IS TRUE"),
    )
    op.execute("ALTER TYPE validationresult ADD VALUE IF NOT EXISTS 'WARNING'")


def downgrade() -> None:
    op.drop_index(
        "uq_affiliate_import_batches_current",
        table_name="affiliate_import_batches",
        postgresql_where=sa.text("is_current IS TRUE"),
    )
    op.drop_column("affiliate_import_batches", "is_current")
    # PostgreSQL does not support removing an enum value safely in place.