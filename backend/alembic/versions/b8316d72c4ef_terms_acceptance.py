"""Persist first terms acceptance without fabricating legacy consent.

Revision ID: b8316d72c4ef
Revises: a72e903d418f
"""

from alembic import op
import sqlalchemy as sa

revision = "b8316d72c4ef"
down_revision = "a72e903d418f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("terms_accepted_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("terms_version", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("terms_snapshot", sa.JSON(), nullable=True))
    op.create_check_constraint(
        "ck_users_terms_complete",
        "users",
        "(terms_accepted_at IS NULL AND terms_version IS NULL AND terms_snapshot IS NULL) OR "
        "(terms_accepted_at IS NOT NULL AND terms_version IS NOT NULL AND terms_snapshot IS NOT NULL)",
    )


def downgrade():
    op.drop_constraint("ck_users_terms_complete", "users", type_="check")
    op.drop_column("users", "terms_snapshot")
    op.drop_column("users", "terms_version")
    op.drop_column("users", "terms_accepted_at")
