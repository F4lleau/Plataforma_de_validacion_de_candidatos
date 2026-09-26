"""Add unlock requests for admin review.

Revision ID: e4a1c9f7d2b6
Revises: b8316d72c4ef
"""

from alembic import op
import sqlalchemy as sa

revision = "e4a1c9f7d2b6"
down_revision = "b8316d72c4ef"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "unlock_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_unlock_requests_id"), "unlock_requests", ["id"])
    op.create_index(
        op.f("ix_unlock_requests_user_id"), "unlock_requests", ["user_id"]
    )
    op.create_index(op.f("ix_unlock_requests_email"), "unlock_requests", ["email"])
    op.create_index(op.f("ix_unlock_requests_status"), "unlock_requests", ["status"])
    op.create_index(
        "uq_unlock_requests_pending_user",
        "unlock_requests",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade():
    op.drop_index("uq_unlock_requests_pending_user", table_name="unlock_requests")
    op.drop_index(op.f("ix_unlock_requests_status"), table_name="unlock_requests")
    op.drop_index(op.f("ix_unlock_requests_email"), table_name="unlock_requests")
    op.drop_index(op.f("ix_unlock_requests_user_id"), table_name="unlock_requests")
    op.drop_index(op.f("ix_unlock_requests_id"), table_name="unlock_requests")
    op.drop_table("unlock_requests")
