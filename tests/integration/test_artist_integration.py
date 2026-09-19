from pathlib import Path

import pytest

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.contracts import PaintingPlan
from painting_agents.mcp.client import PaintingMCPClient

@pytest.mark.asyncio
async def test_artist_can_paint_through_mcp() -> None:
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

        result = await artist.paint(plan)

        assert result.shapes_created

        canvas = await mcp_client.get_canvas()

        assert canvas["shapes"]

        shape_ids = {shape["id"] for shape in canvas["shapes"]}

        assert set(result.shapes_created).issubset(shape_ids)

    finally:
        await mcp_client.close()