"""Enforce electoral date and position coherence without changing legacy rows."""
from alembic import op
revision = 'e271bb89a403'
down_revision = 'dc5da19db749'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint('ck_election_loading_dates', 'elections', '(loading_opens IS NULL AND loading_closes IS NULL) OR (loading_opens IS NOT NULL AND loading_closes IS NOT NULL AND loading_opens <= loading_closes AND loading_closes <= election_date)')
    op.create_check_constraint('ck_office_positions', 'offices', 'required_positions > 0')


def downgrade():
    op.drop_constraint('ck_office_positions', 'offices', type_='check')
    op.drop_constraint('ck_election_loading_dates', 'elections', type_='check')
