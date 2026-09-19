from langchain_core.tools import StructuredTool

from painting_agents.mcp.tools.canvas import CanvasTools


def create_artist_tools(canvas_tools: CanvasTools) -> list[StructuredTool]:
    """Create the tools available to an Artist agent."""

    return [
        StructuredTool.from_function(
            func=canvas_tools.add_circle,
            name="add_circle",
            description=(
                "Add a circle to the painting. "
                "Use this for circular objects such as the sun, moon, "
                "or decorative elements."
            ),
        ),
        StructuredTool.from_function(
            func=canvas_tools.add_rectangle,
            name="add_rectangle",
            description=(
                "Add a rectangle to the painting. "
                "Use this for buildings, walls, ground areas, "
                "and other rectangular objects."
            ),
        ),
        StructuredTool.from_function(
            func=canvas_tools.add_line,
            name="add_line",
            description=(
                "Add a line to the painting. "
                "Use this for mountains, roads, horizons, "
                "branches, outlines, and other linear elements."
            ),
        ),
        StructuredTool.from_function(
            func=canvas_tools.remove_shape,
            name="remove_shape",
            description=(
                "Remove an existing shape from the painting by its ID."
            ),
        ),
    ]