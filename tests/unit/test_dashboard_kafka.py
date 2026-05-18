"""
Tests for Kafka event publishing triggered by DashboardService.

Events expected:
  - stats.academic-performance-alert  → when any subject is at_risk or failing
  - stats.academic-overload-alert     → when gpa_trend is "declining" AND overdue tasks > 0
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.application.service.dashboard_service import DashboardService

# ── helpers ───────────────────────────────────────────────────────────────────

_SUBJECT_FAILING = {
    "id": "sub-fail",
    "name": "Física I",
    "code": "FIS101",
    "credits": 3,
    "evaluations": [
        {
            "id": "e1",
            "name": "Parcial",
            "weight": 1.0,
            "grade": 2.0,
            "date": "2026-03-01",
        }
    ],
}

_SUBJECT_AT_RISK = {
    "id": "sub-risk",
    "name": "Química",
    "code": "QUI101",
    "credits": 3,
    "evaluations": [
        {
            "id": "e1",
            "name": "Parcial",
            "weight": 1.0,
            "grade": 3.2,
            "date": "2026-03-01",
        }
    ],
}

_SUBJECT_PASSING = {
    "id": "sub-pass",
    "name": "Cálculo I",
    "code": "MAT101",
    "credits": 4,
    "evaluations": [
        {
            "id": "e1",
            "name": "Parcial",
            "weight": 1.0,
            "grade": 4.5,
            "date": "2026-03-01",
        }
    ],
}

# 4 graded evaluations are needed to compute a non-stable GPA trend
_SUBJECTS_DECLINING = [
    {
        "id": "sub-d",
        "name": "Materia",
        "code": "M1",
        "credits": 3,
        "evaluations": [
            {
                "id": "e1",
                "name": "P1",
                "weight": 0.25,
                "grade": 4.5,
                "date": "2026-01-10",
            },
            {
                "id": "e2",
                "name": "P2",
                "weight": 0.25,
                "grade": 4.0,
                "date": "2026-02-10",
            },
            {
                "id": "e3",
                "name": "P3",
                "weight": 0.25,
                "grade": 2.5,
                "date": "2026-03-10",
            },
            {
                "id": "e4",
                "name": "P4",
                "weight": 0.25,
                "grade": 2.0,
                "date": "2026-04-10",
            },
        ],
    }
]


def _make_service(subjects, tasks):
    academic = MagicMock()
    academic.get_subjects = AsyncMock(return_value=subjects)
    task_client = MagicMock()
    task_client.get_tasks = AsyncMock(return_value=tasks)
    return DashboardService(academic, task_client)


# ── performance alert ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_performance_alert_published_when_subject_is_failing():
    service = _make_service([_SUBJECT_FAILING], [])
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_dashboard("u1", "tok")
        assert result.failing_subjects == 1
        topics = [call.args[0] for call in mock_pub.call_args_list]
        assert any("performance" in t for t in topics)


@pytest.mark.asyncio
async def test_performance_alert_published_when_subject_is_at_risk():
    service = _make_service([_SUBJECT_AT_RISK], [])
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_dashboard("u1", "tok")
        assert result.at_risk_subjects == 1
        topics = [call.args[0] for call in mock_pub.call_args_list]
        assert any("performance" in t for t in topics)


@pytest.mark.asyncio
async def test_no_performance_alert_when_all_subjects_passing():
    service = _make_service([_SUBJECT_PASSING], [])
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_dashboard("u1", "tok")
        assert result.failing_subjects == 0
        assert result.at_risk_subjects == 0
        topics = [call.args[0] for call in mock_pub.call_args_list]
        assert not any("performance" in t for t in topics)


# ── overload alert ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_overload_alert_published_when_declining_trend_and_overdue_tasks():
    overdue_task = {"id": "t1", "subject_id": "sub-d", "status": "OVERDUE"}
    service = _make_service(_SUBJECTS_DECLINING, [overdue_task])
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_dashboard("u1", "tok")
        assert result.gpa_trend == "declining"
        assert result.tasks.overdue == 1
        topics = [call.args[0] for call in mock_pub.call_args_list]
        assert any("overload" in t for t in topics)


@pytest.mark.asyncio
async def test_no_overload_alert_when_trend_declining_but_no_overdue():
    service = _make_service(_SUBJECTS_DECLINING, [])
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_dashboard("u1", "tok")
        assert result.gpa_trend == "declining"
        assert result.tasks.overdue == 0
        topics = [call.args[0] for call in mock_pub.call_args_list]
        assert not any("overload" in t for t in topics)


@pytest.mark.asyncio
async def test_no_overload_alert_when_overdue_but_trend_stable():
    overdue_task = {"id": "t1", "subject_id": "sub-pass", "status": "OVERDUE"}
    service = _make_service([_SUBJECT_PASSING], [overdue_task])
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_dashboard("u1", "tok")
        assert result.gpa_trend == "stable"
        topics = [call.args[0] for call in mock_pub.call_args_list]
        assert not any("overload" in t for t in topics)


# ── no events at all ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_events_published_when_all_conditions_clean():
    completed_task = {"id": "t1", "subject_id": "sub-pass", "status": "COMPLETED"}
    service = _make_service([_SUBJECT_PASSING], [completed_task])
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        await service.get_dashboard("u1", "tok")
        mock_pub.assert_not_called()
