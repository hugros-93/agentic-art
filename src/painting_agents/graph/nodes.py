from typing import Any

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.critic import CriticAgent
from painting_agents.agents.director import DirectorAgent
from painting_agents.graph.state import PaintingGraphState
from painting_agents.mcp.client import PaintingMCPClient


class PaintingGraphNodes:
    def __init__(
        self,
        *,
        mcp_client: PaintingMCPClient,
        director: DirectorAgent,
        artist: ArtistAgent,
        critic: CriticAgent,
    ) -> None:
        self.mcp_client = mcp_client
        self.director = director
        self.artist = artist
        self.critic = critic

    async def director_node(
        self,
        state: PaintingGraphState,
    ) -> dict[str, Any]:
        request = state.get("request")
        if request is None:
            raise ValueError("Painting request is required.")

        plan = self.director.create_plan(request)

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

        previous_critique = state.get("critique")

        critique_text = None

        if previous_critique is not None:
            critique_text = previous_critique.model_dump_json(indent=2)

        result = await self.artist.paint(
            plan,
            critique=critique_text,
        )

        return {
            "artist_result": result,
            "iteration": state.get("iteration", 0) + 1,
        }

    async def critic_node(
        self,
        state: PaintingGraphState,
    ) -> dict[str, Any]:
        plan = state.get("plan")
        if plan is None:
            raise ValueError("Painting plan is required before critique.")

        canvas = await self.mcp_client.get_canvas()

        critique = self.critic.critique(
            plan,
            canvas,
        )

        return {
            "critique": critique,
        }