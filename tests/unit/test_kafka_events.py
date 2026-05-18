from dataclasses import asdict

import pytest

from app.infrastructure.messaging.events import (
    AcademicOverloadAlertEvent,
    AcademicPerformanceAlertEvent,
    StudySuggestionEvent,
)

# ── AcademicPerformanceAlertEvent ─────────────────────────────────────────────


def test_performance_event_type():
    event = AcademicPerformanceAlertEvent(
        user_id="u1", overall_gpa=3.5, failing_subjects=1, at_risk_subjects=0
    )
    assert event.event_type == "ACADEMIC_PERFORMANCE_ALERT"


def test_performance_event_has_timestamp():
    event = AcademicPerformanceAlertEvent(
        user_id="u1", overall_gpa=3.5, failing_subjects=1, at_risk_subjects=0
    )
    assert isinstance(event.timestamp, str)
    assert len(event.timestamp) > 0


def test_performance_event_default_empty_subjects_list():
    event = AcademicPerformanceAlertEvent(
        user_id="u1", overall_gpa=2.8, failing_subjects=1, at_risk_subjects=0
    )
    assert event.subjects_at_risk == []


def test_performance_event_stores_subjects_at_risk():
    subjects = [
        {
            "subject_id": "s1",
            "subject_name": "Math",
            "status": "failing",
            "current_average": 2.5,
        }
    ]
    event = AcademicPerformanceAlertEvent(
        user_id="u1",
        overall_gpa=3.0,
        failing_subjects=1,
        at_risk_subjects=0,
        subjects_at_risk=subjects,
    )
    assert len(event.subjects_at_risk) == 1
    assert event.subjects_at_risk[0]["subject_id"] == "s1"


def test_performance_event_serializable_with_asdict():
    event = AcademicPerformanceAlertEvent(
        user_id="u1",
        overall_gpa=3.5,
        failing_subjects=0,
        at_risk_subjects=1,
        subjects_at_risk=[{"subject_id": "s1", "status": "at_risk"}],
    )
    d = asdict(event)
    assert d["user_id"] == "u1"
    assert d["event_type"] == "ACADEMIC_PERFORMANCE_ALERT"
    assert d["overall_gpa"] == 3.5
    assert d["at_risk_subjects"] == 1
    assert "timestamp" in d
    assert d["subjects_at_risk"][0]["subject_id"] == "s1"


# ── AcademicOverloadAlertEvent ────────────────────────────────────────────────


def test_overload_event_type():
    event = AcademicOverloadAlertEvent(
        user_id="u1", overdue_tasks=3, gpa_trend="declining", failing_subjects=1
    )
    assert event.event_type == "ACADEMIC_OVERLOAD_ALERT"


def test_overload_event_has_timestamp():
    event = AcademicOverloadAlertEvent(
        user_id="u1", overdue_tasks=2, gpa_trend="declining", failing_subjects=0
    )
    assert isinstance(event.timestamp, str)


def test_overload_event_serializable():
    event = AcademicOverloadAlertEvent(
        user_id="u1", overdue_tasks=2, gpa_trend="declining", failing_subjects=0
    )
    d = asdict(event)
    assert d["overdue_tasks"] == 2
    assert d["gpa_trend"] == "declining"
    assert d["failing_subjects"] == 0


# ── StudySuggestionEvent ──────────────────────────────────────────────────────


def test_study_suggestion_event_type():
    event = StudySuggestionEvent(
        user_id="u1",
        subject_id="s1",
        subject_name="Physics",
        trend="declining",
        current_average=2.5,
    )
    assert event.event_type == "STUDY_SUGGESTION"


def test_study_suggestion_has_timestamp():
    event = StudySuggestionEvent(
        user_id="u1",
        subject_id="s1",
        subject_name="Physics",
        trend="declining",
        current_average=2.5,
    )
    assert isinstance(event.timestamp, str)
    assert len(event.timestamp) > 0


def test_study_suggestion_serializable():
    event = StudySuggestionEvent(
        user_id="u1",
        subject_id="s1",
        subject_name="Physics",
        trend="declining",
        current_average=2.8,
    )
    d = asdict(event)
    assert d["subject_id"] == "s1"
    assert d["subject_name"] == "Physics"
    assert d["current_average"] == pytest.approx(2.8)
    assert d["trend"] == "declining"


def test_each_event_instance_has_independent_timestamp():
    e1 = AcademicPerformanceAlertEvent(
        user_id="u1", overall_gpa=3.0, failing_subjects=0, at_risk_subjects=1
    )
    e2 = AcademicPerformanceAlertEvent(
        user_id="u2", overall_gpa=3.0, failing_subjects=0, at_risk_subjects=1
    )
    assert isinstance(e1.timestamp, str)
    assert isinstance(e2.timestamp, str)
