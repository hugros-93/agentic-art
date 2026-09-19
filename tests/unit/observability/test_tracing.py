from painting_agents.observability.tracing import (
    configure_tracing,
    get_tracer,
)


def test_tracer_can_create_span() -> None:
    configure_tracing()

    tracer = get_tracer("test")

    with tracer.start_as_current_span("test.span"):
        pass