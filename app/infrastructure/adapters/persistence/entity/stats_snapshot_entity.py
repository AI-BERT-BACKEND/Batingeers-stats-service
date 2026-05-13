import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DashboardSnapshotEntity(Base):
    __tablename__ = "dashboard_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    overall_gpa: Mapped[float] = mapped_column(Float, nullable=False)
    gpa_trend: Mapped[str] = mapped_column(String(20), nullable=False)
    total_subjects: Mapped[int] = mapped_column(Integer, nullable=False)
    passing_subjects: Mapped[int] = mapped_column(Integer, nullable=False)
    at_risk_subjects: Mapped[int] = mapped_column(Integer, nullable=False)
    failing_subjects: Mapped[int] = mapped_column(Integer, nullable=False)
    subjects_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    tasks_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )


class SubjectSnapshotEntity(Base):
    __tablename__ = "subject_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject_name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_code: Mapped[str] = mapped_column(String(50), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    current_average: Mapped[float] = mapped_column(Float, nullable=False)
    max_possible_grade: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_needed: Mapped[float | None] = mapped_column(Float, nullable=True)
    trend: Mapped[str] = mapped_column(String(20), nullable=False)
    tasks_total: Mapped[int] = mapped_column(Integer, nullable=False)
    tasks_completed: Mapped[int] = mapped_column(Integer, nullable=False)
    tasks_pending: Mapped[int] = mapped_column(Integer, nullable=False)
    tasks_overdue: Mapped[int] = mapped_column(Integer, nullable=False)
    task_completion_rate: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    projected_grade: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    grade_history_data: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    related_tasks_data: Mapped[list] = mapped_column(JSONB, nullable=True, default=list)
    chart_data: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
