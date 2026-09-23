from __future__ import annotations

from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from painting_agents.config import Settings

_initialized = False


def configure_tracing(settings: Settings) -> None:
    """Configure OpenTelemetry tracing."""

    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        insecure=True,
    )

    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)


def flush_tracing() -> None:
    provider = trace.get_tracer_provider()

    if isinstance(provider, TracerProvider):
        provider.force_flush()


def get_tracer(
    name: str = "painting-agents",
) -> trace.Tracer:
    return trace.get_tracer(name)


def set_span_attributes(
    span: trace.Span,
    attributes: dict[str, Any],
) -> None:
    for key, value in attributes.items():
        if value is None:
            continue

        if isinstance(value, (str, bool, int, float)):
            span.set_attribute(key, value)


def set_painting_context(
    span: trace.Span,
    *,
    request_id: str | None = None,
    session_id: str | None = None,
    iteration: int | None = None,
) -> None:
    set_span_attributes(
        span,
        {
            "painting.request_id": request_id,
            "painting.session_id": session_id,
            "painting.iteration": iteration,
        },
    )
