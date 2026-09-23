from pathlib import Path
from xml.etree import ElementTree as ET

from painting_agents.domain.canvas import Canvas
from painting_agents.domain.shapes import Circle, Line, Rectangle, Shape

SVG_NAMESPACE = "http://www.w3.org/2000/svg"

ET.register_namespace("", SVG_NAMESPACE)


def _svg_element(tag: str, **attributes: str | int | float) -> ET.Element:
    """Create an SVG element with the SVG namespace."""
    return ET.Element(
        f"{{{SVG_NAMESPACE}}}{tag}",
        {key: str(value) for key, value in attributes.items()},
    )


def _render_shape(parent: ET.Element, shape: Shape) -> None:
    """Render one domain shape into an SVG element."""

    if isinstance(shape, Circle):
        attributes: dict[str, str | int | float] = {
            "id": shape.id,
            "cx": shape.center.x,
            "cy": shape.center.y,
            "r": shape.radius,
            "fill": shape.fill.value,
            "opacity": shape.opacity,
        }

        if shape.stroke is not None:
            attributes["stroke"] = shape.stroke.value

        parent.append(_svg_element("circle", **attributes))
        return

    if isinstance(shape, Rectangle):
        attributes = {
            "id": shape.id,
            "x": shape.position.x,
            "y": shape.position.y,
            "width": shape.width,
            "height": shape.height,
            "fill": shape.fill.value,
            "opacity": shape.opacity,
        }

        if shape.stroke is not None:
            attributes["stroke"] = shape.stroke.value

        parent.append(_svg_element("rect", **attributes))
        return

    if isinstance(shape, Line):
        parent.append(
            _svg_element(
                "line",
                id=shape.id,
                x1=shape.start.x,
                y1=shape.start.y,
                x2=shape.end.x,
                y2=shape.end.y,
                stroke=shape.stroke.value,
                **{"stroke-width": shape.stroke_width},
                opacity=shape.opacity,
            )
        )
        return

    raise TypeError(f"Unsupported shape type: {type(shape).__name__}")


def render_svg(canvas: Canvas) -> str:
    """Render a Canvas as an SVG document."""

    root = _svg_element(
        "svg",
        width=canvas.width,
        height=canvas.height,
        viewBox=f"0 0 {canvas.width} {canvas.height}",
    )

    for shape in sorted(canvas.shapes, key=lambda shape: shape.z_index):
        _render_shape(root, shape)

    return ET.tostring(root, encoding="unicode")


def write_svg(canvas: Canvas, path: str | Path) -> None:
    """Render a Canvas and write the SVG to disk."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_svg(canvas), encoding="utf-8")
