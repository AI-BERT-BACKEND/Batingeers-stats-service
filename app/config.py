from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "stats-service"
    app_port: int = 8085
    app_env: str = "development"

    jwt_secret: str = "default-secret-change-in-production"
    jwt_algorithm: str = "HS256"

    academic_service_url: str = "http://academic-service:8082"
    task_service_url: str = "http://task-service:8083"

    http_timeout: float = 10.0
    http_max_retries: int = 3

    # CORS — comma-separated list of allowed origins. Use ["*"] to allow all (development only).
    cors_allowed_origins: list[str] = ["*"]

    # Kafka — leave unset to disable event publishing entirely
    kafka_bootstrap_servers: str | None = None
    kafka_topic_performance: str = "stats.academic-performance-alert"
    kafka_topic_overload: str = "stats.academic-overload-alert"
    kafka_topic_study_suggestion: str = "stats.study-suggestion"

    # PostgreSQL — asyncpg driver: postgresql+asyncpg://user:pass@host:port/db
    database_url: str | None = None

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()
