"""Invitations and verified email; fail closed on legacy normalized duplicates.

Revision ID: a72e903d418f
Revises: 6cb192ebc9fe
"""

from alembic import op
import sqlalchemy as sa

revision = "a72e903d418f"
down_revision = "6cb192ebc9fe"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    duplicates = connection.execute(
        sa.text(
            "SELECT count(*) FROM (SELECT lower(trim(email)) FROM users GROUP BY lower(trim(email)) HAVING count(*) > 1) collisions"
        )
    ).scalar()
    if duplicates:
        raise RuntimeError(
            "Normalized email collisions detected. Resolve with an authorized operator before retrying; no accounts were merged."
        )
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(), nullable=True))
    op.create_index(
        "uq_users_normalized_email",
        "users",
        [sa.text("lower(btrim(email))")],
        unique=True,
    )
    op.create_table(
        "invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "invited_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("modules", sa.JSON(), nullable=False),
        sa.Column("digest", sa.String(64), nullable=False, unique=True),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_at", sa.DateTime()),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
    )
    for column in ("invited_by", "state", "expires_at"):
        op.create_index(f"ix_invitations_{column}", "invitations", [column])
    op.alter_column("mail_outbox", "user_id", nullable=True)
    op.add_column(
        "mail_outbox",
        sa.Column(
            "invitation_id",
            sa.Integer(),
            sa.ForeignKey("invitations.id", name="fk_mail_outbox_invitation"),
        ),
    )
    op.add_column("mail_outbox", sa.Column("invitation_digest", sa.String(64)))
    op.create_index("ix_mail_outbox_invitation_id", "mail_outbox", ["invitation_id"])


def downgrade():
    # Invitation mails have no User until acceptance; remove only this new kind.
    op.execute("DELETE FROM mail_outbox WHERE invitation_id IS NOT NULL")
    op.drop_index("ix_mail_outbox_invitation_id", table_name="mail_outbox")
    op.drop_column("mail_outbox", "invitation_digest")
    op.drop_constraint("fk_mail_outbox_invitation", "mail_outbox", type_="foreignkey")
    op.drop_column("mail_outbox", "invitation_id")
    op.alter_column("mail_outbox", "user_id", nullable=False)
    op.drop_table("invitations")
    op.drop_index("uq_users_normalized_email", table_name="users")
    op.drop_column("users", "email_verified_at")
