"""
Tests for Kafka event publishing triggered by SubjectStatsService.

Event expected:
  - stats.study-suggestion  → when the subject's computed trend is "declining"
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from com.aibert.dosw.application.service.subject_stats_service import (
    SubjectStatsService,
)

# ── helpers ───────────────────────────────────────────────────────────────────

# 3 graded evaluations are sufficient for _compute_trend to classify as declining
_SUBJECT_DECLINING = {
    "id": "sub-1",
    "name": "Física I",
    "code": "FIS101",
    "credits": 3,
    "evaluations": [
        {"id": "e1", "name": "P1", "weight": 0.3, "grade": 4.5, "date": "2026-01-01"},
        {"id": "e2", "name": "P2", "weight": 0.3, "grade": 3.0, "date": "2026-02-01"},
        {"id": "e3", "name": "P3", "weight": 0.4, "grade": 2.0, "date": "2026-03-01"},
    ],
}

_SUBJECT_IMPROVING = {
    "id": "sub-2",
    "name": "Cálculo I",
    "code": "MAT101",
    "credits": 4,
    "evaluations": [
        {"id": "e1", "name": "P1", "weight": 0.3, "grade": 2.5, "date": "2026-01-01"},
        {"id": "e2", "name": "P2", "weight": 0.3, "grade": 3.5, "date": "2026-02-01"},
        {"id": "e3", "name": "P3", "weight": 0.4, "grade": 4.8, "date": "2026-03-01"},
    ],
}

_SUBJECT_STABLE = {
    "id": "sub-3",
    "name": "Programación I",
    "code": "INF101",
    "credits": 3,
    "evaluations": [
        {"id": "e1", "name": "P1", "weight": 0.5, "grade": 4.0, "date": "2026-01-01"},
        {"id": "e2", "name": "P2", "weight": 0.5, "grade": 4.0, "date": "2026-02-01"},
    ],
}

_SUBJECT_NO_GRADES = {
    "id": "sub-4",
    "name": "Historia",
    "code": "HIS101",
    "credits": 2,
    "evaluations": [
        {"id": "e1", "name": "P1", "weight": 1.0, "grade": None, "date": None},
    ],
}


def _make_service(subject):
    academic = MagicMock()
    academic.get_subject = AsyncMock(return_value=subject)
    task_client = MagicMock()
    task_client.get_tasks_by_subject = AsyncMock(return_value=[])
    return SubjectStatsService(academic, task_client)


# ── study suggestion ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_study_suggestion_published_when_trend_is_declining():
    service = _make_service(_SUBJECT_DECLINING)
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_subject_stats("u1", "sub-1", "tok")
        assert result.trend == "declining"
        mock_pub.assert_called_once()
        topic = mock_pub.call_args[0][0]
        assert "study-suggestion" in topic


@pytest.mark.asyncio
async def test_study_suggestion_event_contains_correct_user_and_subject():
    service = _make_service(_SUBJECT_DECLINING)
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        await service.get_subject_stats("user-xyz", "sub-1", "tok")
        event_arg = mock_pub.call_args[0][1]
        assert event_arg.user_id == "user-xyz"
        assert event_arg.subject_id == "sub-1"
        assert event_arg.subject_name == "Física I"
        assert event_arg.trend == "declining"


@pytest.mark.asyncio
async def test_no_event_published_when_trend_is_improving():
    service = _make_service(_SUBJECT_IMPROVING)
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_subject_stats("u1", "sub-2", "tok")
        assert result.trend == "improving"
        mock_pub.assert_not_called()


@pytest.mark.asyncio
async def test_no_event_published_when_trend_is_stable():
    service = _make_service(_SUBJECT_STABLE)
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_subject_stats("u1", "sub-3", "tok")
        assert result.trend == "stable"
        mock_pub.assert_not_called()


@pytest.mark.asyncio
async def test_no_event_published_when_no_grades():
    service = _make_service(_SUBJECT_NO_GRADES)
    with patch(
        "app.infrastructure.messaging.kafka_producer.publish_event", new=AsyncMock()
    ) as mock_pub:
        result = await service.get_subject_stats("u1", "sub-4", "tok")
        assert result.trend == "stable"
        mock_pub.assert_not_called()
