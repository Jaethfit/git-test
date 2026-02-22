from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pipelines = relationship("Pipeline", back_populates="resume", cascade="all, delete-orphan")


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_title = Column(String(255), nullable=False)
    keywords = Column(JSON, nullable=True)
    location = Column(String(255), nullable=True)
    remote_ok = Column(Boolean, default=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="pipelines")
    jobs = relationship("Job", back_populates="pipeline", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    external_id = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    salary_range = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(1024), nullable=False)
    source = Column(String(50), nullable=True)
    match_score = Column(Float, default=0.0)
    match_breakdown = Column(JSON, nullable=True)
    requires_cover_letter = Column(Boolean, default=False)
    screening_questions = Column(JSON, nullable=True)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pipeline = relationship("Pipeline", back_populates="jobs")
    application = relationship("Application", back_populates="job", uselist=False, cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    tailored_resume_keywords = Column(JSON, nullable=True)
    cover_letter = Column(Text, nullable=True)
    screening_answers = Column(JSON, nullable=True)
    status = Column(String(50), default="ready")  # ready, submitted, viewed, interview, offer, rejected
    auto_apply_eligible = Column(Boolean, default=False)
    submitted_at = Column(DateTime, nullable=True)
    last_status_change = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True)

    job = relationship("Job", back_populates="application")
