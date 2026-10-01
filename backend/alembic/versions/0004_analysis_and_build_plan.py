"""Analysis and build plan migration

Revision ID: 0004_analysis_and_build
Revises: 0003_runs_and_sources
Create Date: 2026-10-01 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0004_analysis_and_build'
down_revision: Union[str, None] = '0003_runs_and_sources'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. evidence
    op.create_table(
        'evidence',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('char_start', sa.Integer(), nullable=True),
        sa.Column('char_end', sa.Integer(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['run_id'], ['research_runs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_source_id'), 'evidence', ['source_id'], unique=False)

    # 2. claims
    op.create_table(
        'claims',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('question_id', sa.String(length=36), nullable=True),
        sa.Column('critic_flags', sa.JSON(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['run_id'], ['research_runs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_claims_project_id'), 'claims', ['project_id'], unique=False)

    # 3. claim_evidence
    op.create_table(
        'claim_evidence',
        sa.Column('claim_id', sa.String(length=36), nullable=False),
        sa.Column('evidence_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['claim_id'], ['claims.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidence.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('claim_id', 'evidence_id')
    )

    # 4. gaps
    op.create_table(
        'gaps',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('gap_type', sa.String(length=50), nullable=False),
        sa.Column('classification', sa.String(length=50), nullable=False, server_default='INFERENCE'),
        sa.Column('confidence', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('requires_human_verification', sa.Boolean(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['run_id'], ['research_runs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gaps_project_id'), 'gaps', ['project_id'], unique=False)

    # 5. gap_claims
    op.create_table(
        'gap_claims',
        sa.Column('gap_id', sa.String(length=36), nullable=False),
        sa.Column('claim_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['gap_id'], ['gaps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['claim_id'], ['claims.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('gap_id', 'claim_id')
    )

    # 6. proposals
    op.create_table(
        'proposals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('feasibility', sa.JSON(), nullable=False),
        sa.Column('gap_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proposals_project_id'), 'proposals', ['project_id'], unique=False)

    # 7. architectures
    op.create_table(
        'architectures',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('components', sa.JSON(), nullable=False),
        sa.Column('data_flow', sa.JSON(), nullable=False),
        sa.Column('tech_stack', sa.JSON(), nullable=False),
        sa.Column('mermaid', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('proposal_id')
    )

    # 8. mvp_tasks
    op.create_table(
        'mvp_tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('tier', sa.String(length=20), nullable=False, server_default='mvp'),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('est_hours', sa.Float(), nullable=False, server_default='4.0'),
        sa.Column('depends_on', sa.JSON(), nullable=False),
        sa.Column('skill_tags', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mvp_tasks_proposal_id'), 'mvp_tasks', ['proposal_id'], unique=False)

    # 9. risks
    op.create_table(
        'risks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('proposal_id', sa.String(length=36), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('mitigation', sa.Text(), nullable=False, server_default=''),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risks_proposal_id'), 'risks', ['proposal_id'], unique=False)

    # 10. idea_challenges
    op.create_table(
        'idea_challenges',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('run_id', sa.String(length=36), nullable=True),
        sa.Column('idea_text', sa.Text(), nullable=False),
        sa.Column('related_work', sa.JSON(), nullable=False),
        sa.Column('issues', sa.JSON(), nullable=False),
        sa.Column('differentiation', sa.JSON(), nullable=False),
        sa.Column('suggested_investigation', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_idea_challenges_project_id'), 'idea_challenges', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_table('idea_challenges')
    op.drop_table('risks')
    op.drop_table('mvp_tasks')
    op.drop_table('architectures')
    op.drop_table('proposals')
    op.drop_table('gap_claims')
    op.drop_table('gaps')
    op.drop_table('claim_evidence')
    op.drop_table('claims')
    op.drop_table('evidence')
