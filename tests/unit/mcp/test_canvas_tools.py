import pytest

from painting_agents.domain.factory import create_painting_session
from painting_agents.mcp.tools.canvas import CanvasTools


@pytest.fixture
def tools() -> CanvasTools:
    session = create_painting_session(
        title="Test Painting",
        width=1024,
        height=768,
    )
    return CanvasTools(session)


def test_add_circle(tools: CanvasTools) -> None:
    result = tools.add_circle(
        shape_id="sun",
        x=500,
        y=150,
        radius=75,
        fill="#FFD700",
    )

    assert result["success"] is True

    circle = result["shape"]
    assert circle["id"] == "sun"
    assert circle["type"] == "circle"
    assert circle["center"]["x"] == 500
    assert circle["center"]["y"] == 150
    assert circle["radius"] == 75
    assert circle["fill"]["value"] == "#FFD700"

    result = tools.get_canvas()
    assert len(result["shapes"]) == 1

def test_add_rectangle(tools: CanvasTools) -> None:
    result = tools.add_rectangle(
        shape_id="house",
        x=100,
        y=300,
        width=300,
        height=200,
        fill="#8B4513",
    )

    assert result["success"] is True

    rectangle = result["shape"]
    assert rectangle["id"] == "house"
    assert rectangle["type"] == "rectangle"
    assert rectangle["width"] == 300
    assert rectangle["height"] == 200
    assert rectangle["fill"]["value"] == "#8B4513"

    result = tools.get_canvas()
    assert len(result["shapes"]) == 1


def test_add_line(tools: CanvasTools) -> None:
    result = tools.add_line(
        shape_id="ground",
        start_x=0,
        start_y=600,
        end_x=1024,
        end_y=600,
        stroke="#000000",
        stroke_width=3,
    )

    assert result["success"] is True

    line = result["shape"]
    assert line["id"] == "ground"
    assert line["type"] == "line"
    assert line["start"]["x"] == 0
    assert line["start"]["y"] == 600
    assert line["end"]["x"] == 1024
    assert line["end"]["y"] == 600
    assert line["stroke"]["value"] == "#000000"
    assert line["stroke_width"] == 3

    result = tools.get_canvas()
    assert len(result["shapes"]) == 1

def test_remove_shape(tools: CanvasTools) -> None:
    tools.add_circle(
        shape_id="sun",
        x=500,
        y=150,
        radius=75,
        fill="#FFD700",
    )

    result = tools.remove_shape("sun")

    assert result == {
        "success": True,
        "shape_id": "sun",
    }

    result = tools.get_canvas()

    assert result["shapes"] == []

def test_duplicate_shape_id_is_rejected(tools: CanvasTools) -> None:
    tools.add_circle(
        shape_id="sun",
        x=500,
        y=150,
        radius=75,
        fill="#FFD700",
    )

    with pytest.raises(ValueError, match="Shape already exists"):
        tools.add_circle(
            shape_id="sun",
            x=600,
            y=200,
            radius=50,
            fill="#FF0000",
        )