import json
import logging
import re
from dataclasses import asdict

try:
    from aiokafka import AIOKafkaProducer
except ImportError:  # pragma: no cover
    AIOKafkaProducer = None  # type: ignore[assignment,misc]

from com.aibert.dosw.config import settings

logger = logging.getLogger(__name__)

_producer = None


def _parse_event_hubs_bootstrap(connection_string: str) -> str:
    """Extracts the bootstrap server (host:9093) from an Azure Event Hubs connection string."""
    match = re.search(r"Endpoint=sb://([^/]+)/", connection_string)
    if not match:
        raise ValueError(
            "Invalid KAFKA_CONNECTION_STRING: cannot parse Event Hubs namespace."
        )
    return f"{match.group(1)}:9093"


async def start_producer() -> None:
    global _producer
    if not settings.kafka_connection_string and not settings.kafka_bootstrap_servers:
        logger.info("Kafka not configured — event publishing is disabled")
        return
    try:
        if settings.kafka_connection_string:
            # Azure Event Hubs — SASL/SSL with the connection string as password
            bootstrap = _parse_event_hubs_bootstrap(settings.kafka_connection_string)
            _producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap,
                security_protocol="SASL_SSL",
                sasl_mechanism="PLAIN",
                sasl_plain_username="$ConnectionString",
                sasl_plain_password=settings.kafka_connection_string,
                value_serializer=lambda v: json.dumps(v).encode(),
            )
            logger.info("Kafka producer started — Azure Event Hubs: %s", bootstrap)
        else:
            # Plain Kafka
            _producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode(),
            )
            logger.info(
                "Kafka producer started — brokers: %s", settings.kafka_bootstrap_servers
            )
        await _producer.start()
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
