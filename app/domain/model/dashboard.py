from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SubjectSummary:
    subject_id: str
    name: str
    code: str
    credits: int
    current_average: float
    status: str  # "passing" | "at_risk" | "failing"


@dataclass
class TaskSummary:
    total: int
    completed: int
    pending: int
    overdue: int
    completion_rate: float


@dataclass
class DashboardStats:
    user_id: str
    overall_gpa: float
    gpa_trend: str  # "improving" | "declining" | "stable"
    total_subjects: int
    passing_subjects: int
    at_risk_subjects: int
    failing_subjects: int
    subjects: list[SubjectSummary]
    tasks: TaskSummary
    generated_at: datetime = field(default_factory=datetime.utcnow)
