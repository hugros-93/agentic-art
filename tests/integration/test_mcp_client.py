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


@pytest.mark.asyncio
async def test_mcp_canvas_state_persists_between_tool_calls() -> None:
    project_root = Path(__file__).resolve().parents[2]
    server_script = project_root / "scripts" / "run_mcp_server.py"

    client = PaintingMCPClient(server_script)
    tools = await client.get_tools()

    add_circle = next(tool for tool in tools if tool.name == "add_circle")
    get_canvas = next(tool for tool in tools if tool.name == "get_canvas")

    add_result = await add_circle.ainvoke(
        {
            "shape_id": "sun",
            "x": 500,
            "y": 150,
            "radius": 75,
            "fill": "#FFD700",
        }
    )

    parsed_add = parse_mcp_result(add_result)

    assert parsed_add["success"] is True

    canvas_result = await get_canvas.ainvoke({})
    canvas = parse_mcp_result(canvas_result)

    assert len(canvas["shapes"]) == 1
    assert canvas["shapes"][0]["id"] == "sun"
