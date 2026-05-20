from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AcademicPerformanceAlertEvent:
    """
    Fired when one or more subjects are at risk or failing.
    Consumed by the notification service to send a low-performance alert to the student.
    """

    user_id: str
    overall_gpa: float
    failing_subjects: int
    at_risk_subjects: int
    subjects_at_risk: list[dict] = field(default_factory=list)
    event_type: str = "ACADEMIC_PERFORMANCE_ALERT"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class AcademicOverloadAlertEvent:
    """
    Fired when the student has overdue tasks combined with a declining GPA trend.
    Consumed by the notification service to send an academic overload warning.
    """

    user_id: str
    overdue_tasks: int
    gpa_trend: str
    failing_subjects: int
    event_type: str = "ACADEMIC_OVERLOAD_ALERT"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class StudySuggestionEvent:
    """
    Fired when a specific subject's grade trend is declining.
    Consumed by the notification service to suggest focused study for that subject.
    """

    user_id: str
    subject_id: str
    subject_name: str
    trend: str
    current_average: float
    event_type: str = "STUDY_SUGGESTION"
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
