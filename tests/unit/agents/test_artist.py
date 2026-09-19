from painting_agents.agents.tools import create_artist_tools
from painting_agents.domain.factory import create_painting_session
from painting_agents.mcp.tools.canvas import CanvasTools


def test_artist_tools_are_created() -> None:
    session = create_painting_session(
        title="Test Painting",
        width=1024,
        height=768,
    )
    canvas_tools = CanvasTools(session)

    tools = create_artist_tools(canvas_tools)

    tool_names = {tool.name for tool in tools}

    assert tool_names == {
        "add_circle",
        "add_rectangle",
        "add_line",
        "remove_shape",
    }


def test_add_circle_tool_mutates_canvas() -> None:
    session = create_painting_session(
        title="Test Painting",
        width=1024,
        height=768,
    )
    canvas_tools = CanvasTools(session)

    tools = create_artist_tools(canvas_tools)
    add_circle = next(
        tool for tool in tools if tool.name == "add_circle"
    )

    result = add_circle.invoke(
        {
            "shape_id": "sun",
            "x": 500,
            "y": 150,
            "radius": 75,
            "fill": "#FFD700",
        }
    )

    assert result["success"] is True
    assert result["shape"]["id"] == "sun"

    canvas = session.painting.canvas
    assert len(canvas.shapes) == 1
    assert canvas.shapes[0].id == "sun"