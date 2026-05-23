from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "stats-service"
    app_port: int = 1506
    app_env: str = "development"

    jwt_secret: str = "default-secret-change-in-production"
    jwt_algorithm: str = "HS256"

    academic_service_url: str = "https://academic-service:1502"
    task_service_url: str = "https://task-service:1503"

    http_timeout: float = 10.0
    http_max_retries: int = 3

    # CORS — comma-separated list of allowed origins. Use ["*"] to allow all (development only).
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4200",
        "https://frontend-umber-seven-28.vercel.app",
    ]

    # Kafka — leave unset to disable event publishing entirely.
    # For Azure Event Hubs: set KAFKA_CONNECTION_STRING (bootstrap server is derived automatically).
    # For plain Kafka: set KAFKA_BOOTSTRAP_SERVERS only.
    kafka_bootstrap_servers: str | None = None
    kafka_connection_string: str | None = None
    kafka_topic_performance: str = "stats.academic-performance-alert"
    kafka_topic_overload: str = "stats.academic-overload-alert"
    kafka_topic_study_suggestion: str = "stats.study-suggestion"

    # PostgreSQL — asyncpg driver: postgresql+asyncpg://user:pass@host:port/db
    database_url: str | None = None

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()
