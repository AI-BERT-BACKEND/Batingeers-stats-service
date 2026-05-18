import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import app.infrastructure.messaging.kafka_producer as kp
from app.infrastructure.messaging.events import (
    AcademicPerformanceAlertEvent,
    StudySuggestionEvent,
)
from app.infrastructure.messaging.kafka_producer import (
    publish_event,
    start_producer,
    stop_producer,
)


@pytest.fixture(autouse=True)
def reset_producer():
    """Ensure the global producer is None before and after every test."""
    kp._producer = None
    yield
    kp._producer = None


# ── publish_event ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_event_is_noop_when_no_producer():
    """With _producer = None, publish_event silently skips without raising."""
    event = StudySuggestionEvent(
        user_id="u1",
        subject_id="s1",
        subject_name="Math",
        trend="declining",
        current_average=2.5,
    )
    await publish_event("some.topic", event)  # must not raise


@pytest.mark.asyncio
async def test_publish_event_calls_send_and_wait():
    """When a producer is active, publish_event forwards the event to it."""
    mock_producer = MagicMock()
    mock_producer.send_and_wait = AsyncMock()
    kp._producer = mock_producer

    event = StudySuggestionEvent(
        user_id="u1",
        subject_id="s1",
        subject_name="Math",
        trend="declining",
        current_average=2.5,
    )
    await publish_event("stats.study-suggestion", event)

    mock_producer.send_and_wait.assert_called_once()
    topic_arg = mock_producer.send_and_wait.call_args[0][0]
    assert topic_arg == "stats.study-suggestion"


@pytest.mark.asyncio
async def test_publish_event_passes_event_as_dict():
    """publish_event serializes the dataclass to a dict before sending."""
    mock_producer = MagicMock()
    mock_producer.send_and_wait = AsyncMock()
    kp._producer = mock_producer

    event = AcademicPerformanceAlertEvent(
        user_id="user-42",
        overall_gpa=2.8,
        failing_subjects=1,
        at_risk_subjects=0,
    )
    await publish_event("stats.academic-performance-alert", event)

    payload = mock_producer.send_and_wait.call_args[0][1]
    assert isinstance(payload, dict)
    assert payload["user_id"] == "user-42"
    assert payload["failing_subjects"] == 1


@pytest.mark.asyncio
async def test_publish_event_swallows_producer_exception():
    """If the producer's send raises, publish_event catches it and does not re-raise."""
    mock_producer = MagicMock()
    mock_producer.send_and_wait = AsyncMock(side_effect=Exception("broker timeout"))
    kp._producer = mock_producer

    event = StudySuggestionEvent(
        user_id="u1",
        subject_id="s1",
        subject_name="Math",
        trend="declining",
        current_average=2.5,
    )
    await publish_event("stats.study-suggestion", event)  # must not raise


# ── start_producer ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_start_producer_noop_when_no_brokers_configured():
    """start_producer does nothing when kafka_bootstrap_servers is not set."""
    with patch("app.infrastructure.messaging.kafka_producer.settings") as mock_settings:
        mock_settings.kafka_bootstrap_servers = None
        await start_producer()
        assert kp._producer is None


@pytest.mark.asyncio
async def test_start_producer_handles_connection_failure_gracefully():
    """If aiokafka raises during start, the exception is caught and _producer stays None."""
    with patch("app.infrastructure.messaging.kafka_producer.settings") as mock_settings:
        mock_settings.kafka_bootstrap_servers = "localhost:9092"
        with patch(
            "app.infrastructure.messaging.kafka_producer.AIOKafkaProducer",
            side_effect=ImportError,
        ):
            await start_producer()
            assert kp._producer is None


# ── stop_producer ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_stop_producer_safe_when_no_producer():
    """stop_producer does not raise when no producer was ever started."""
    kp._producer = None
    await stop_producer()  # must not raise


@pytest.mark.asyncio
async def test_stop_producer_calls_stop_on_active_producer():
    """stop_producer calls .stop() on the active producer and resets _producer to None."""
    mock_producer = MagicMock()
    mock_producer.stop = AsyncMock()
    kp._producer = mock_producer

    await stop_producer()

    mock_producer.stop.assert_called_once()
    assert kp._producer is None
