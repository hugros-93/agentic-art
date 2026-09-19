from mcp.server.fastmcp import FastMCP

from painting_agents.domain.canvas import Canvas
from painting_agents.mcp.tools.canvas import CanvasTools

from painting_agents.domain.factory import create_painting_session

mcp = FastMCP("painting-tools")

_session = create_painting_session(
    title="Untitled Painting",
    width=1024,
    height=768,
)

_tools = CanvasTools(_session)


@mcp.tool()
def add_circle(
    shape_id: str,
    x: float,
    y: float,
    radius: float,
    fill: str,
    stroke: str | None = None,
) -> dict:
    """Add a circle to the painting canvas."""

    result = _tools.add_circle(
        shape_id=shape_id,
        x=x,
        y=y,
        radius=radius,
        fill=fill,
        stroke=stroke,
    )

    return result


@mcp.tool()
def add_rectangle(
    shape_id: str,
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    stroke: str | None = None,
) -> dict:
    """Add a rectangle to the painting canvas."""

    result = _tools.add_rectangle(
        shape_id=shape_id,
        x=x,
        y=y,
        width=width,
        height=height,
        fill=fill,
        stroke=stroke,
    )

    return result


@mcp.tool()
def add_line(
    shape_id: str,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    stroke: str,
    stroke_width: float = 1.0,
) -> dict:
    """Add a line to the painting canvas."""

    result = _tools.add_line(
        shape_id=shape_id,
        start_x=start_x,
        start_y=start_y,
        end_x=end_x,
        end_y=end_y,
        stroke=stroke,
        stroke_width=stroke_width,
    )

    return result


@mcp.tool()
def remove_shape(shape_id: str) -> dict:
    """Remove a shape from the painting canvas."""

    _tools.remove_shape(shape_id)

    return {
        "success": True,
        "shape_id": shape_id,
    }


@mcp.tool()
def get_canvas() -> dict:
    return _tools.get_canvas()


if __name__ == "__main__":
    mcp.run()