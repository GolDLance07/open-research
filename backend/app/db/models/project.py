import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    competition_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    rules_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    judging_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    team_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    team_skills: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    time_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    hardware: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft"
    )  # 'draft','analyzed','researching','complete','failed'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    user = relationship("User", back_populates="projects")
    requirements = relationship(
        "Requirement",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Requirement.position",
    )
    research_questions = relationship(
        "ResearchQuestion",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ResearchQuestion.position",
    )
    research_runs = relationship(
        "ResearchRun",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    sources = relationship(
        "Source",
        back_populates="project",
        cascade="all, delete-orphan",
    )
