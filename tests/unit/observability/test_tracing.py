from opentelemetry import trace

from painting_agents.config import Settings
from painting_agents.observability.tracing import configure_tracing


def test_tracer_can_create_span() -> None:

    configure_tracing(Settings())

    tracer = trace.get_tracer("test")

    with tracer.start_as_current_span("test-span") as span:
        assert span.is_recording()