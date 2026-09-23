from pathlib import Path
from typing import Any
from uuid import uuid4
import asyncio
import httpx

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.critic import CriticAgent
from painting_agents.agents.director import DirectorAgent
from painting_agents.config import Settings
from painting_agents.domain.canvas import Canvas
from painting_agents.exceptions import LLMRateLimitError
from painting_agents.graph.workflow import build_painting_graph
from painting_agents.mcp.client import PaintingMCPClient
from painting_agents.observability.langchain import (
    OpenTelemetryCallbackHandler,
)
from painting_agents.observability.tracing import (
    configure_tracing,
    flush_tracing,
    get_tracer,
)
from painting_agents.rendering.png import render_png


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

    settings = Settings()

    # MUST happen before creating painting.run.
    configure_tracing(settings)

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
                director=DirectorAgent(
                    model=None,
                ),
                artist=ArtistAgent(
                    tools=tools,
                ),
                critic=CriticAgent(),
                output_dir=(output_path.parent / output_path.stem),
            )

            result: dict[str, Any] | None = None

            for attempt in range(settings.painting_max_retries + 1):
                try:
                    result = await graph.ainvoke(
                        {
                            "request": request,
                            "request_id": request_id,
                            "max_iterations": max_iterations,
                        }
                    )
                    break

                except LLMRateLimitError:
                    if attempt >= settings.painting_max_retries:
                        raise

                    delay = (
                        settings.painting_retry_delay_seconds
                        * (2**attempt)
                    )

                    span.add_event(
                        "painting.retry",
                        {
                            "reason": "llm_rate_limit",
                            "attempt": attempt + 1,
                            "max_retries": settings.painting_max_retries,
                            "delay_seconds": delay,
                        },
                    )

                    await asyncio.sleep(delay)

                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code != 429:
                        raise

                    if attempt >= settings.painting_max_retries:
                        raise LLMRateLimitError(
                            "LLM provider rate limit exceeded "
                            "after retries."
                        ) from exc

                    delay = (
                        settings.painting_retry_delay_seconds
                        * (2**attempt)
                    )

                    span.add_event(
                        "painting.retry",
                        {
                            "reason": "llm_rate_limit",
                            "attempt": attempt + 1,
                            "max_retries": settings.painting_max_retries,
                            "delay_seconds": delay,
                        },
                    )

                    await asyncio.sleep(delay)

            if result is None:
                raise RuntimeError(
                    "Painting graph completed without producing a result."
                )

            canvas_data = await mcp_client.get_canvas()
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