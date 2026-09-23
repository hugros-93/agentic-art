from pathlib import Path

import cairosvg

from painting_agents.domain.canvas import Canvas
from painting_agents.rendering.svg import render_svg


def render_png(
    canvas: Canvas,
    output_path: Path,
) -> None:
    svg = render_svg(canvas)

    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(output_path),
    )
