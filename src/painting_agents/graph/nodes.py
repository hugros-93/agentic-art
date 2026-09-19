from typing import Any
from pathlib import Path

from painting_agents.domain.canvas import Canvas
from painting_agents.rendering.png import render_png
from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.critic import CriticAgent
from painting_agents.agents.director import DirectorAgent
from painting_agents.graph.state import PaintingGraphState
from painting_agents.mcp.client import PaintingMCPClient
from painting_agents.observability.tracing import (
    get_tracer,
    set_painting_context,
    set_span_attributes,
)

tracer = get_tracer(__name__)


class PaintingGraphNodes:
    def __init__(
        self,
        *,
        mcp_client: PaintingMCPClient,
        director: DirectorAgent,
        artist: ArtistAgent,
        critic: CriticAgent,
        output_dir: Path,
    ) -> None:
        self.mcp_client = mcp_client
        self.director = director
        self.artist = artist
        self.critic = critic
        self.output_dir = output_dir

    async def director_node(
        self,
        state: PaintingGraphState,
    ) -> dict[str, Any]:
        request = state.get("request")
        if request is None:
            raise ValueError("Painting request is required.")

        with tracer.start_as_current_span("agent.director") as span:
            set_span_attributes(
                span,
                {
                    "agent.name": "director",
                    "agent.type": "director",
                    "painting.request": request,
                },
            )

            plan = self.director.create_plan(request)

            span.set_attribute(
                "painting.plan.title",
                plan.title,
            )

            return {
                "plan": plan,
                "iteration": 0,
            }

    async def artist_node(
        self,
        state: PaintingGraphState,
    ) -> dict[str, Any]:
        plan = state.get("plan")

        if plan is None:
            raise ValueError("Painting plan is required before artist execution.")

        iteration = state.get("iteration", 0)

        previous_critique = state.get("critique")
        critique_text = None

        if previous_critique is not None:
            critique_text = previous_critique.model_dump_json(indent=2)

        with tracer.start_as_current_span("agent.artist") as span:
            set_span_attributes(
                span,
                {
                    "agent.name": "artist",
                    "agent.type": "artist",
                    "painting.iteration": iteration,
                    "painting.plan.title": plan.title,
                },
            )

            result = await self.artist.paint(
                plan,
                critique=critique_text,
            )

            span.set_attribute(
                "painting.shapes_created",
                len(result.shapes_created),
            )

            return {
                "artist_result": result,
                "iteration": iteration + 1,
            }

    async def render_node(
        self,
        state: PaintingGraphState,
    ) -> dict[str, Any]:
        iteration = state.get("iteration", 0)

        with tracer.start_as_current_span("rendering.painting") as span:
            set_span_attributes(
                span,
                {
                    "rendering.format": "png",
                    "painting.iteration": iteration,
                },
            )

            set_painting_context(
                span,
                request_id=state.get("request_id"),
                iteration=iteration,
            )

            canvas_data = await self.mcp_client.get_canvas()
            canvas = Canvas.model_validate(canvas_data)

            iteration_path = (
                self.output_dir
                / f"iteration-{iteration:03d}.png"
            )

            self.output_dir.mkdir(parents=True, exist_ok=True)
            render_png(canvas, iteration_path)

            span.set_attribute(
                "rendering.output_path",
                str(iteration_path),
            )
            span.set_attribute(
                "rendering.shape_count",
                len(canvas.shapes),
            )

            return {
                "image_path": str(iteration_path),
            }


    async def critic_node(
        self,
        state: PaintingGraphState,
    ) -> dict[str, Any]:
        plan = state.get("plan")

        if plan is None:
            raise ValueError("Painting plan is required before critique.")

        with tracer.start_as_current_span("agent.critic") as span:
            set_span_attributes(
                span,
                {
                    "agent.name": "critic",
                    "agent.type": "critic",
                    "painting.iteration": state.get("iteration", 0),
                    "painting.plan.title": plan.title,
                },
            )

            canvas = await self.mcp_client.get_canvas()

            critique = self.critic.critique(
                plan,
                canvas,
            )

            span.set_attribute(
                "critique.approved",
                critique.approved,
            )

            span.set_attribute(
                "critique.issue_count",
                len(critique.issues),
            )

            return {
                "critique": critique,
            }