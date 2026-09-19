from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from painting_agents.domain.factory import create_painting_session
from painting_agents.mcp.tools.canvas import CanvasTools

def test_add_circle_creates_mcp_span() -> None:
    exporter = InMemorySpanExporter()

    provider = TracerProvider()
    provider.add_span_processor(
        SimpleSpanProcessor(exporter)
    )

    trace.set_tracer_provider(provider)

    session = create_painting_session(title="Test painting")
    tools = CanvasTools(
        session,
        agent_id="artist",
    )

    result = tools.add_circle(
        shape_id="sun",
        x=500,
        y=200,
        radius=100,
        fill="#FFD700",
    )

    assert result["success"] is True

    spans = exporter.get_finished_spans()

    mcp_spans = [
        span
        for span in spans
        if span.name == "mcp.add_circle"
    ]

    assert len(mcp_spans) == 1

    span = mcp_spans[0]

    attributes = span.attributes
    assert attributes is not None

    assert attributes["mcp.tool"] == "add_circle"
    assert attributes["painting.agent_id"] == "artist"
    assert attributes["painting.shape_id"] == "sun"
    assert attributes["painting.radius"] == 100
    assert attributes["painting.fill"] == "#FFD700"
    assert attributes["mcp.success"] is True