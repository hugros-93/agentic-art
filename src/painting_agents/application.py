from pathlib import Path
from typing import Any
from uuid import uuid4

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.critic import CriticAgent
from painting_agents.agents.director import DirectorAgent
from painting_agents.graph.workflow import build_painting_graph
from painting_agents.mcp.client import PaintingMCPClient
from painting_agents.rendering.png import render_png
from painting_agents.observability.tracing import (
    configure_tracing,
    get_tracer,
    flush_tracing,
)
from painting_agents.observability.langchain import (
    OpenTelemetryCallbackHandler,
)

otel_callback = OpenTelemetryCallbackHandler()

tracer = get_tracer(__name__)


async def create_painting(
    request: str,
    *,
    server_script: Path,
    output_path: Path,
    max_iterations: int = 2,
    request_id: str | None = None,
) -> dict[str, Any]:
    if request_id is None:
        request_id = str(uuid4())

    # MUST happen before creating painting.run.
    configure_tracing()

    with tracer.start_as_current_span("painting.run") as span:
        span.set_attribute(
            "painting.request_id",
            request_id,
        )
        span.set_attribute(
            "painting.request",
            request,
        )
        span.set_attribute(
            "painting.max_iterations",
            max_iterations,
        )

        mcp_client = PaintingMCPClient(server_script)

        try:
            tools = await mcp_client.get_tools()

            graph = build_painting_graph(
                mcp_client=mcp_client,
                director=DirectorAgent(),
                artist=ArtistAgent(
                    tools=tools,
                ),
                critic=CriticAgent(),
                output_dir=(output_path.parent / output_path.stem),
            )

            result = await graph.ainvoke(
                {
                    "request": request,
                    "request_id": request_id,
                    "max_iterations": max_iterations,
                }
            )

            canvas_data = await mcp_client.get_canvas()

            from painting_agents.domain.canvas import Canvas

            canvas = Canvas.model_validate(canvas_data)

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            render_png(
                canvas,
                output_path,
            )

            critique = result.get("critique")

            if critique is not None:
                span.set_attribute(
                    "painting.approved",
                    critique.approved,
                )

            span.set_attribute(
                "painting.shape_count",
                len(canvas.shapes),
            )

            return result

        finally:
            await mcp_client.close()
            flush_tracing()
