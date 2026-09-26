"""Add admin configuration relations and office types.

Revision ID: f2b7a61d9c30
Revises: e4a1c9f7d2b6
"""

from alembic import op
import sqlalchemy as sa

revision = "f2b7a61d9c30"
down_revision = "e4a1c9f7d2b6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "office_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.execute(
        "INSERT INTO office_types (code, name, active) VALUES "
        "('electivo', 'Electivo', true), ('partidario', 'Partidario', true)"
    )
    op.add_column("offices", sa.Column("office_type_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_offices_office_type_id"), "offices", ["office_type_id"])
    op.create_foreign_key(
        "fk_offices_office_type_id",
        "offices",
        "office_types",
        ["office_type_id"],
        ["id"],
    )
    op.execute(
        "UPDATE offices SET office_type_id = (SELECT id FROM office_types WHERE code = 'electivo') "
        "WHERE office_type_id IS NULL"
    )

    op.create_table(
        "election_offices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("election_id", sa.Integer(), nullable=False),
        sa.Column("office_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["election_id"], ["elections.id"]),
        sa.ForeignKeyConstraint(["office_id"], ["offices.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("election_id", "office_id"),
    )
    op.create_index(
        op.f("ix_election_offices_election_id"),
        "election_offices",
        ["election_id"],
    )
    op.create_index(
        op.f("ix_election_offices_office_id"), "election_offices", ["office_id"]
    )
    op.execute(
        "INSERT INTO election_offices (election_id, office_id) "
        "SELECT DISTINCT election_id, office_id FROM election_rules"
    )

    op.create_table(
        "election_municipalities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("election_id", sa.Integer(), nullable=False),
        sa.Column("municipality_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["election_id"], ["elections.id"]),
        sa.ForeignKeyConstraint(["municipality_id"], ["municipalities.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("election_id", "municipality_id"),
    )
    op.create_index(
        op.f("ix_election_municipalities_election_id"),
        "election_municipalities",
        ["election_id"],
    )
    op.create_index(
        op.f("ix_election_municipalities_municipality_id"),
        "election_municipalities",
        ["municipality_id"],
    )


def downgrade():
    op.drop_index(
        op.f("ix_election_municipalities_municipality_id"),
        table_name="election_municipalities",
    )
    op.drop_index(
        op.f("ix_election_municipalities_election_id"),
        table_name="election_municipalities",
    )
    op.drop_table("election_municipalities")
    op.drop_index(op.f("ix_election_offices_office_id"), table_name="election_offices")
    op.drop_index(
        op.f("ix_election_offices_election_id"), table_name="election_offices"
    )
    op.drop_table("election_offices")
    op.drop_constraint("fk_offices_office_type_id", "offices", type_="foreignkey")
    op.drop_index(op.f("ix_offices_office_type_id"), table_name="offices")
    op.drop_column("offices", "office_type_id")
    op.drop_table("office_types")
