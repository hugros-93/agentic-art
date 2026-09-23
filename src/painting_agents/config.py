from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Provider
    llm_provider: str = "mistral" #"ollama"

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "ministral-3:3b"
    ollama_temperature: float = 0.2

    # Mistral (API)
    mistral_api_key: SecretStr | None = None
    mistral_model: str = "mistral-medium-latest"
    mistral_temperature: float = 0.2
    mistral_max_retries: int = 3

    # OpenTelemetry
    otel_service_name: str = "painting-agents"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    # Painting retry
    painting_max_retries: int = 2
    painting_retry_delay_seconds: float = 10.0