from pathlib import Path

from painting_agents.domain.canvas import Canvas
from painting_agents.domain.shapes import Circle, Color, Point
from painting_agents.rendering.png import render_png


def test_render_png(tmp_path: Path) -> None:
    canvas = Canvas(width=400, height=300)

    canvas.add_shape(
        Circle(
            id="sun",
            center=Point(x=200, y=100),
            radius=50,
            fill=Color(value="#FDB813"),
        )
    )

    output_path = tmp_path / "painting.png"

    render_png(canvas, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0