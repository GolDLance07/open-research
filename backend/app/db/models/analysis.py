import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Table, Column, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now

# Association table for claim <-> evidence
claim_evidence_table = Table(
    "claim_evidence",
    Base.metadata,
    Column("claim_id", String(36), ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", String(36), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for gap <-> claims
gap_claims_table = Table(
    "gap_claims",
    Base.metadata,
    Column("gap_id", String(36), ForeignKey("gaps.id", ondelete="CASCADE"), primary_key=True),
    Column("claim_id", String(36), ForeignKey("claims.id", ondelete="CASCADE"), primary_key=True),
)


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("research_runs.id", ondelete="SET NULL"), nullable=True)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    char_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    source = relationship("Source")
    claims = relationship("Claim", secondary=claim_evidence_table, back_populates="evidence")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("research_runs.id", ondelete="SET NULL"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # FACT, DIRECTLY_SUPPORTED, SYNTHESIS, INFERENCE, HYPOTHESIS
    confidence: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    question_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    critic_flags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    evidence = relationship("Evidence", secondary=claim_evidence_table, back_populates="claims")
    gaps = relationship("Gap", secondary=gap_claims_table, back_populates="claims")


class Gap(Base):
    __tablename__ = "gaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("research_runs.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    gap_type: Mapped[str] = mapped_column(String(50), nullable=False)  # limitation, contradiction, underexplored, opportunity
    classification: Mapped[str] = mapped_column(String(50), default="INFERENCE")
    confidence: Mapped[str] = mapped_column(String(20), default="medium")
    requires_human_verification: Mapped[bool] = mapped_column(Boolean, default=True)

    claims = relationship("Claim", secondary=gap_claims_table, back_populates="gaps")


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    feasibility: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    gap_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    architecture = relationship("Architecture", uselist=False, cascade="all, delete-orphan")
    mvp_tasks = relationship("MVPTask", cascade="all, delete-orphan", order_by="MVPTask.sequence")
    risks = relationship("Risk", cascade="all, delete-orphan")


class Architecture(Base):
    __tablename__ = "architectures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), unique=True)
    components: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    data_flow: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    tech_stack: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    mermaid: Mapped[str] = mapped_column(Text, nullable=False)


class MVPTask(Base):
    __tablename__ = "mvp_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), index=True)
    tier: Mapped[str] = mapped_column(String(20), default="mvp")  # mvp, stretch
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    est_hours: Mapped[float] = mapped_column(Float, default=4.0)
    depends_on: Mapped[List[str]] = mapped_column(JSON, default=list)
    skill_tags: Mapped[List[str]] = mapped_column(JSON, default=list)


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    mitigation: Mapped[str] = mapped_column(Text, default="")


class IdeaChallenge(Base):
    __tablename__ = "idea_challenges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    idea_text: Mapped[str] = mapped_column(Text, nullable=False)
    related_work: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    issues: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    differentiation: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    suggested_investigation: Mapped[List[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
