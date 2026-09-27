"""add padron circuits

Revision ID: 1f4a9b7c2d10
Revises: f2b7a61d9c30
Create Date: 2026-09-27 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1f4a9b7c2d10"
down_revision: Union[str, Sequence[str], None] = "f2b7a61d9c30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "padron_circuits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("section", sa.String(length=100), nullable=True),
        sa.Column("section_code", sa.String(length=50), nullable=True),
        sa.Column("source_batch_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["source_batch_id"], ["affiliate_import_batches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_padron_circuits_id"), "padron_circuits", ["id"])
    op.create_index(op.f("ix_padron_circuits_name"), "padron_circuits", ["name"])
    op.create_index(op.f("ix_padron_circuits_code"), "padron_circuits", ["code"])
    op.create_index(op.f("ix_padron_circuits_section"), "padron_circuits", ["section"])
    op.create_index(
        op.f("ix_padron_circuits_section_code"),
        "padron_circuits",
        ["section_code"],
    )
    op.create_index(
        op.f("ix_padron_circuits_source_batch_id"),
        "padron_circuits",
        ["source_batch_id"],
    )
    op.create_unique_constraint(
        "uq_padron_circuits_batch_section_code_circuit_code",
        "padron_circuits",
        ["source_batch_id", "section_code", "code", "name"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_padron_circuits_batch_section_code_circuit_code",
        "padron_circuits",
        type_="unique",
    )
    op.drop_index(op.f("ix_padron_circuits_source_batch_id"), table_name="padron_circuits")
    op.drop_index(op.f("ix_padron_circuits_section_code"), table_name="padron_circuits")
    op.drop_index(op.f("ix_padron_circuits_section"), table_name="padron_circuits")
    op.drop_index(op.f("ix_padron_circuits_code"), table_name="padron_circuits")
    op.drop_index(op.f("ix_padron_circuits_name"), table_name="padron_circuits")
    op.drop_index(op.f("ix_padron_circuits_id"), table_name="padron_circuits")
    op.drop_table("padron_circuits")
