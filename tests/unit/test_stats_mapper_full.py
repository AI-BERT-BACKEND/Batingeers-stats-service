from datetime import date, datetime

import pytest

from app.application.mapper.stats_mapper import dashboard_to_dto, subject_stats_to_dto
from app.application.utility.chart_generator import ChartPoint
from app.domain.model.dashboard import DashboardStats, SubjectSummary, TaskSummary
from app.domain.model.subject_stats import GradeEntry, SubjectStats


def _make_dashboard(user_id="u-1") -> DashboardStats:
    return DashboardStats(
        user_id=user_id,
        overall_gpa=3.9,
        gpa_trend="improving",
        total_subjects=2,
        passing_subjects=1,
        at_risk_subjects=1,
        failing_subjects=0,
        subjects=[
            SubjectSummary(
                subject_id="sub-1",
                name="Cálculo",
                code="MAT101",
                credits=4,
                current_average=4.2,
                status="passing",
            ),
            SubjectSummary(
                subject_id="sub-2",
                name="Física",
                code="FIS101",
                credits=3,
                current_average=3.1,
                status="at_risk",
            ),
        ],
        tasks=TaskSummary(
            total=5,
            completed=3,
            pending=1,
            overdue=1,
            completion_rate=60.0,
        ),
        generated_at=datetime(2026, 4, 10, 12, 0),
    )


def _make_subject_stats() -> SubjectStats:
    return SubjectStats(
        subject_id="sub-1",
        subject_name="Cálculo I",
        subject_code="MAT101",
        credits=4,
        grade_history=[
            GradeEntry("e1", "Parcial 1", 0.3, 4.5, date(2026, 3, 15), 1.35),
            GradeEntry("e2", "Parcial 2", 0.3, 3.0, date(2026, 4, 15), 0.9),
            GradeEntry("e3", "Final", 0.4, None, None, 0.0),
        ],
        current_average=3.75,
        max_possible_grade=4.75,
        minimum_needed=1.875,
        projected_grade=2.25,
        trend="stable",
        tasks_total=3,
        tasks_completed=1,
        tasks_pending=1,
        tasks_overdue=1,
        task_completion_rate=33.33,
        status="passing",
        related_tasks=[
            {
                "id": "t1",
                "title": "Tarea 1",
                "status": "COMPLETED",
                "dueDate": "2026-04-01",
                "subject_id": "sub-1",
            },
            {
                "id": "t2",
                "title": "Tarea 2",
                "status": "PENDING",
                "due_date": "2026-03-15",
                "subjectId": "sub-1",
            },
        ],
        chart_data=[
            ChartPoint(week_label="2026-W11", average=4.5, evaluations_count=1),
            ChartPoint(week_label="2026-W16", average=3.75, evaluations_count=2),
        ],
        generated_at=datetime(2026, 4, 10, 12, 0),
    )


# ── dashboard_to_dto ──────────────────────────────────────────────────────────


def test_dashboard_dto_user_id():
    dto = dashboard_to_dto(_make_dashboard("u-99"))
    assert dto.user_id == "u-99"


def test_dashboard_dto_gpa():
    dto = dashboard_to_dto(_make_dashboard())
    assert dto.overall_gpa == pytest.approx(3.9, rel=0.001)


def test_dashboard_dto_gpa_trend():
    dto = dashboard_to_dto(_make_dashboard())
    assert dto.gpa_trend == "improving"


def test_dashboard_dto_subjects_count():
    dto = dashboard_to_dto(_make_dashboard())
    assert dto.total_subjects == 2
    assert dto.passing_subjects == 1
    assert dto.at_risk_subjects == 1
    assert dto.failing_subjects == 0


def test_dashboard_dto_subjects_list():
    dto = dashboard_to_dto(_make_dashboard())
    assert len(dto.subjects) == 2
    assert dto.subjects[0].subject_id == "sub-1"
    assert dto.subjects[0].current_average == pytest.approx(4.2, rel=0.01)
    assert dto.subjects[0].status == "passing"


def test_dashboard_dto_tasks():
    dto = dashboard_to_dto(_make_dashboard())
    assert dto.tasks.total == 5
    assert dto.tasks.completed == 3
    assert dto.tasks.pending == 1
    assert dto.tasks.overdue == 1
    assert dto.tasks.completion_rate == pytest.approx(60.0, rel=0.01)


def test_dashboard_dto_generated_at():
    dto = dashboard_to_dto(_make_dashboard())
    assert dto.generated_at is not None


# ── subject_stats_to_dto ──────────────────────────────────────────────────────


def test_subject_dto_ids():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert dto.subject_id == "sub-1"
    assert dto.subject_name == "Cálculo I"
    assert dto.subject_code == "MAT101"
    assert dto.credits == 4


def test_subject_dto_averages():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert dto.current_average == pytest.approx(3.75, rel=0.01)
    assert dto.max_possible_grade == pytest.approx(4.75, rel=0.01)
    assert dto.minimum_needed == pytest.approx(1.875, rel=0.01)
    assert dto.projected_grade == pytest.approx(2.25, rel=0.01)


def test_subject_dto_trend_and_status():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert dto.trend == "stable"
    assert dto.status == "passing"


def test_subject_dto_task_counts():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert dto.tasks_total == 3
    assert dto.tasks_completed == 1
    assert dto.tasks_pending == 1
    assert dto.tasks_overdue == 1
    assert dto.task_completion_rate == pytest.approx(33.33, rel=0.01)


def test_subject_dto_grade_history():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert len(dto.grade_history) == 3
    assert dto.grade_history[0].evaluation_id == "e1"
    assert dto.grade_history[0].grade == pytest.approx(4.5)
    assert dto.grade_history[0].weight == pytest.approx(0.3)
    assert dto.grade_history[0].contribution == pytest.approx(1.35, rel=0.01)


def test_subject_dto_grade_history_null_grade():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert dto.grade_history[2].grade is None
    assert dto.grade_history[2].evaluation_date is None


def test_subject_dto_chart_data():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert len(dto.chart_data) == 2
    assert dto.chart_data[0].week_label == "2026-W11"
    assert dto.chart_data[0].average == pytest.approx(4.5)
    assert dto.chart_data[0].evaluations_count == 1


def test_subject_dto_related_tasks_with_camel_case_keys():
    dto = subject_stats_to_dto(_make_subject_stats())
    assert len(dto.related_tasks) == 2
    # First task uses camelCase keys
    t1 = dto.related_tasks[0]
    assert t1.task_id == "t1"
    assert t1.status == "COMPLETED"
    assert t1.due_date == "2026-04-01"


def test_subject_dto_related_tasks_with_snake_case_keys():
    dto = subject_stats_to_dto(_make_subject_stats())
    t2 = dto.related_tasks[1]
    assert t2.task_id == "t2"
    assert t2.due_date == "2026-03-15"


def test_subject_dto_related_tasks_subject_id_camel():
    dto = subject_stats_to_dto(_make_subject_stats())
    t2 = dto.related_tasks[1]
    # second task has subjectId (camelCase)
    assert t2.subject_id == "sub-1"


def test_subject_dto_no_related_tasks():
    stats = _make_subject_stats()
    stats.related_tasks = []
    dto = subject_stats_to_dto(stats)
    assert dto.related_tasks == []


def test_subject_dto_empty_chart_data():
    stats = _make_subject_stats()
    stats.chart_data = []
    dto = subject_stats_to_dto(stats)
    assert dto.chart_data == []
