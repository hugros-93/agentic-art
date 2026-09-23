from pathlib import Path

import pytest

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.contracts import PaintingPlan
from painting_agents.agents.critic import CriticAgent
from painting_agents.mcp.client import PaintingMCPClient


@pytest.mark.asyncio
async def test_critic_evaluates_artist_canvas() -> None:
    project_root = Path(__file__).resolve().parents[2]
    server_script = project_root / "scripts" / "run_mcp_server.py"

    mcp_client = PaintingMCPClient(server_script)

    try:
        tools = await mcp_client.get_tools()

        artist = ArtistAgent(tools=tools)

        plan = PaintingPlan(
            title="Simple sunset",
            description="A simple sunset over the ground.",
            style="minimal geometric",
        )

        artist_result = await artist.paint(plan)

        assert artist_result.shapes_created

        canvas = await mcp_client.get_canvas()

        critic = CriticAgent()
        critique = critic.critique(plan, canvas)

        assert critique.assessment
        assert isinstance(critique.approved, bool)

    finally:
        await mcp_client.close()
