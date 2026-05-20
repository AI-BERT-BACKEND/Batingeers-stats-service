import json
import logging
from dataclasses import asdict

try:
    from aiokafka import AIOKafkaProducer
except ImportError:  # pragma: no cover
    AIOKafkaProducer = None  # type: ignore[assignment,misc]

from com.aibert.dosw.config import settings

logger = logging.getLogger(__name__)

_producer = None


async def start_producer() -> None:
    global _producer
    if not settings.kafka_bootstrap_servers:
        logger.info("Kafka not configured — event publishing is disabled")
        return
    try:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        await _producer.start()
        logger.info(
            "Kafka producer started — brokers: %s", settings.kafka_bootstrap_servers
        )
    except Exception as exc:
        logger.warning("Failed to start Kafka producer: %s", exc)
        _producer = None


async def stop_producer() -> None:
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish_event(topic: str, event) -> None:
    if _producer is None:
        logger.debug("Kafka unavailable — skipping event on topic '%s'", topic)
        return
    try:
        await _producer.send_and_wait(topic, asdict(event))
        logger.debug("Published event to topic '%s'", topic)
    except Exception as exc:
        logger.warning("Failed to publish event to topic '%s': %s", topic, exc)
