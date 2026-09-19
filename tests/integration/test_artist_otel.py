from pathlib import Path

import pytest

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.contracts import PaintingPlan
from painting_agents.mcp.client import PaintingMCPClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_artist_real_execution(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    server_script = (
        project_root
        / "scripts"
        / "run_mcp_server.py"
    )

    mcp_client = PaintingMCPClient(server_script)

    try:
        tools = await mcp_client.get_tools()

        artist = ArtistAgent(
            tools=tools,
        )

        plan = PaintingPlan(
            title="Simple Sun",
            description="A simple geometric sunset.",
            style="Minimal geometric art."
        )

        result = await artist.paint(plan)

        assert result is not None

        canvas = await mcp_client.get_canvas()

        assert canvas["width"] == 1024
        assert canvas["height"] == 768

        print(
            f"Artist created {len(canvas['shapes'])} shapes."
        )

    finally:
        await mcp_client.close()