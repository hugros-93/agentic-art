from pathlib import Path
from typing import Any

from painting_agents.agents.artist import ArtistAgent
from painting_agents.agents.critic import CriticAgent
from painting_agents.agents.director import DirectorAgent
from painting_agents.graph.workflow import build_painting_graph
from painting_agents.mcp.client import PaintingMCPClient
from painting_agents.rendering.png import render_png


async def create_painting(
    request: str,
    *,
    server_script: Path,
    output_path: Path,
    max_iterations: int = 2,
) -> dict[str, Any]:
    mcp_client = PaintingMCPClient(server_script)

    try:
        tools = await mcp_client.get_tools()

        graph = build_painting_graph(
            mcp_client=mcp_client,
            director=DirectorAgent(),
            artist=ArtistAgent(tools=tools),
            critic=CriticAgent(),
        )

        result = await graph.ainvoke(
            {
                "request": request,
                "max_iterations": max_iterations,
            }
        )

        canvas_data = await mcp_client.get_canvas()

        # The MCP response is already a serialized Canvas.
        # Reconstruct the domain object so the renderer remains
        # independent of MCP.
        from painting_agents.domain.canvas import Canvas

        canvas = Canvas.model_validate(canvas_data)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        render_png(canvas, output_path)

        return result

    finally:
        await mcp_client.close()