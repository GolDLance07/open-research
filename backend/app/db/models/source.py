import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, utc_now


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("research_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'web','paper','repository','model','dataset'
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    snippet: Mapped[str] = mapped_column(Text, nullable=False, default="")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    relevance_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    project = relationship("Project", back_populates="sources")
    run = relationship("ResearchRun", back_populates="sources")

    paper = relationship("Paper", back_populates="source", uselist=False, cascade="all, delete-orphan")
    repository = relationship(
        "Repository", back_populates="source", uselist=False, cascade="all, delete-orphan"
    )
    model = relationship("ModelEntity", back_populates="source", uselist=False, cascade="all, delete-orphan")
    dataset = relationship(
        "DatasetEntity", back_populates="source", uselist=False, cascade="all, delete-orphan"
    )


class Paper(Base):
    __tablename__ = "papers"

    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    citation_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    authors: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    open_access_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source = relationship("Source", back_populates="paper")


class Repository(Base):
    __tablename__ = "repositories"

    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_pushed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    topics: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    readme_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    source = relationship("Source", back_populates="repository")


class ModelEntity(Base):
    __tablename__ = "models"

    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )
    hub_id: Mapped[str] = mapped_column(String(255), nullable=False)
    task: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    params: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source = relationship("Source", back_populates="model")


class DatasetEntity(Base):
    __tablename__ = "datasets"

    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )
    hub_id: Mapped[str] = mapped_column(String(255), nullable=False)
    license: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size_note: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    modality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    access_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    source = relationship("Source", back_populates="dataset")
