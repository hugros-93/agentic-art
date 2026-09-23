from pathlib import Path

import pytest

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.critic import CriticAgent
from painting_agents.agents.director import DirectorAgent
from painting_agents.graph.workflow import build_painting_graph
from painting_agents.mcp.client import PaintingMCPClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_painting_graph_end_to_end(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    server_script = project_root / "scripts" / "run_mcp_server.py"

    mcp_client = PaintingMCPClient(server_script)

    try:
        tools = await mcp_client.get_tools()

        director = DirectorAgent()
        artist = ArtistAgent(tools=tools)
        critic = CriticAgent()

        graph = build_painting_graph(
            mcp_client=mcp_client,
            director=director,
            artist=artist,
            critic=critic,
            output_dir=tmp_path,
        )

        result = await graph.ainvoke(
            {
                "request": (
                    "Create a simple geometric sunset over the ground. "
                    "Use a warm sun in the upper part of the canvas and "
                    "a horizontal ground line near the bottom."
                ),
                "max_iterations": 2,
            }
        )

        assert result["plan"]
        assert result["artist_result"]
        assert result["critique"]

        canvas = await mcp_client.get_canvas()

        assert canvas["shapes"]

        print("\nFinal canvas:")
        print(canvas)

        print("\nCritique:")
        print(result["critique"])

    finally:
        await mcp_client.close()
