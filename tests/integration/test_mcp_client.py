from pathlib import Path

import pytest

from painting_agents.mcp.client import PaintingMCPClient
from painting_agents.mcp.results import parse_mcp_result


@pytest.mark.asyncio
async def test_mcp_client_discovers_painting_tools() -> None:
    project_root = Path(__file__).resolve().parents[2]
    server_script = project_root / "scripts" / "run_mcp_server.py"

    client = PaintingMCPClient(server_script)

    tools = await client.get_tools()

    tool_names = {tool.name for tool in tools}

    assert "add_circle" in tool_names
    assert "add_rectangle" in tool_names
    assert "add_line" in tool_names
    assert "remove_shape" in tool_names
    assert "get_canvas" in tool_names


@pytest.mark.asyncio
async def test_mcp_add_circle() -> None:
    project_root = Path(__file__).resolve().parents[2]
    server_script = project_root / "scripts" / "run_mcp_server.py"

    client = PaintingMCPClient(server_script)
    tools = await client.get_tools()

    add_circle = next(tool for tool in tools if tool.name == "add_circle")

    result = await add_circle.ainvoke(
        {
            "shape_id": "sun",
            "x": 500,
            "y": 150,
            "radius": 75,
            "fill": "#FFD700",
        }
    )

    parsed = parse_mcp_result(result)

    assert parsed["success"] is True
    assert parsed["shape"]["id"] == "sun"
    assert parsed["shape"]["type"] == "circle"