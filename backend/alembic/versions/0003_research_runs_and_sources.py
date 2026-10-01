"""Research runs and sources migration

Revision ID: 0003_runs_and_sources
Revises: 0002_reqs_and_rqs
Create Date: 2026-10-01 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_runs_and_sources'
down_revision: Union[str, None] = '0002_reqs_and_rqs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. research_runs
    op.create_table(
        'research_runs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('kind', sa.String(length=50), nullable=False, server_default='research'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('cycle_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tool_calls', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('model_provider', sa.String(length=50), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=True),
        sa.Column('budget', sa.JSON(), nullable=False),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_runs_project_id'), 'research_runs', ['project_id'], unique=False)

    # 2. run_events
    op.create_table(
        'run_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['run_id'], ['research_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_run_events_run_id'), 'run_events', ['run_id'], unique=False)

    # 3. sources
    op.create_table(
        'sources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('canonical_url', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('published_date', sa.Date(), nullable=True),
        sa.Column('publisher', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('snippet', sa.Text(), nullable=False, server_default=''),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('relevance_note', sa.Text(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False, server_default=''),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['run_id'], ['research_runs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sources_project_id'), 'sources', ['project_id'], unique=False)
    op.create_index(op.f('ix_sources_run_id'), 'sources', ['run_id'], unique=False)

    # 4. papers
    op.create_table(
        'papers',
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('venue', sa.String(length=255), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('citation_count', sa.Integer(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('authors', sa.JSON(), nullable=False),
        sa.Column('open_access_url', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('source_id')
    )

    # 5. repositories
    op.create_table(
        'repositories',
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=100), nullable=True),
        sa.Column('stars', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('forks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_pushed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=False),
        sa.Column('readme_summary', sa.Text(), nullable=True),
        sa.Column('archived', sa.Boolean(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('source_id')
    )

    # 6. models
    op.create_table(
        'models',
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('hub_id', sa.String(length=255), nullable=False),
        sa.Column('task', sa.String(length=100), nullable=True),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('params', sa.String(length=50), nullable=True),
        sa.Column('downloads', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('source_id')
    )

    # 7. datasets
    op.create_table(
        'datasets',
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('hub_id', sa.String(length=255), nullable=False),
        sa.Column('license', sa.String(length=100), nullable=True),
        sa.Column('size_note', sa.String(length=100), nullable=True),
        sa.Column('modality', sa.String(length=100), nullable=True),
        sa.Column('access_note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('source_id')
    )


def downgrade() -> None:
    op.drop_table('datasets')
    op.drop_table('models')
    op.drop_table('repositories')
    op.drop_table('papers')
    op.drop_index(op.f('ix_sources_run_id'), table_name='sources')
    op.drop_index(op.f('ix_sources_project_id'), table_name='sources')
    op.drop_table('sources')
    op.drop_index(op.f('ix_run_events_run_id'), table_name='run_events')
    op.drop_table('run_events')
    op.drop_index(op.f('ix_research_runs_project_id'), table_name='research_runs')
    op.drop_table('research_runs')
