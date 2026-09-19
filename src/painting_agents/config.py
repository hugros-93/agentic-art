from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application configuration."""

    ollama_base_url: str = Field(
        default="http://localhost:11434",
    )
    ollama_model: str = Field(
        # default="qwen3:0.6b",
        default="qwen3:1.7b ",
    )
    ollama_temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    otel_service_name: str = Field(default="painting-agents")
    otel_exporter_otlp_endpoint: str = Field(default="http://localhost:4317")


settings = Settings()
