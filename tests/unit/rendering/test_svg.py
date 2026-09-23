from xml.etree import ElementTree as ET

from painting_agents.domain.canvas import Canvas
from painting_agents.domain.shapes import Circle, Color, Line, Point, Rectangle
from painting_agents.rendering.svg import render_svg, write_svg

SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def test_empty_canvas_renders_svg() -> None:
    canvas = Canvas(width=800, height=600)

    svg = render_svg(canvas)
    root = ET.fromstring(svg)

    assert root.tag == f"{{{SVG_NAMESPACE}}}svg"
    assert root.attrib["width"] == "800"
    assert root.attrib["height"] == "600"
    assert root.attrib["viewBox"] == "0 0 800 600"


def test_circle_is_rendered() -> None:
    canvas = Canvas(width=800, height=600)

    canvas.add_shape(
        Circle(
            id="sun",
            center=Point(x=400, y=200),
            radius=100,
            fill=Color(value="#FFD700"),
        )
    )

    root = ET.fromstring(render_svg(canvas))
    circle = root.find(f"{{{SVG_NAMESPACE}}}circle")

    assert circle is not None
    assert circle.attrib["id"] == "sun"
    assert circle.attrib["cx"] == "400.0"
    assert circle.attrib["cy"] == "200.0"
    assert circle.attrib["r"] == "100.0"
    assert circle.attrib["fill"] == "#FFD700"


def test_rectangle_is_rendered() -> None:
    canvas = Canvas(width=800, height=600)

    canvas.add_shape(
        Rectangle(
            id="house",
            position=Point(x=100, y=200),
            width=300,
            height=200,
            fill=Color(value="#8B4513"),
        )
    )

    root = ET.fromstring(render_svg(canvas))
    rectangle = root.find(f"{{{SVG_NAMESPACE}}}rect")

    assert rectangle is not None
    assert rectangle.attrib["id"] == "house"
    assert rectangle.attrib["x"] == "100.0"
    assert rectangle.attrib["y"] == "200.0"
    assert rectangle.attrib["width"] == "300.0"
    assert rectangle.attrib["height"] == "200.0"
    assert rectangle.attrib["fill"] == "#8B4513"


def test_line_is_rendered() -> None:
    canvas = Canvas(width=800, height=600)

    canvas.add_shape(
        Line(
            id="ground",
            start=Point(x=0, y=500),
            end=Point(x=800, y=500),
            stroke=Color(value="#000000"),
            stroke_width=3,
        )
    )

    root = ET.fromstring(render_svg(canvas))
    line = root.find(f"{{{SVG_NAMESPACE}}}line")

    assert line is not None
    assert line.attrib["id"] == "ground"
    assert line.attrib["x1"] == "0.0"
    assert line.attrib["y1"] == "500.0"
    assert line.attrib["x2"] == "800.0"
    assert line.attrib["y2"] == "500.0"
    assert line.attrib["stroke"] == "#000000"
    assert line.attrib["stroke-width"] == "3.0"


def test_shapes_preserve_canvas_order() -> None:
    canvas = Canvas(width=800, height=600)

    canvas.add_shape(
        Rectangle(
            id="background",
            position=Point(x=0, y=0),
            width=800,
            height=600,
            fill=Color(value="#87CEEB"),
        )
    )

    canvas.add_shape(
        Circle(
            id="sun",
            center=Point(x=600, y=100),
            radius=50,
            fill=Color(value="#FFD700"),
        )
    )

    root = ET.fromstring(render_svg(canvas))
    elements = list(root)

    assert elements[0].attrib["id"] == "background"
    assert elements[1].attrib["id"] == "sun"


def test_optional_stroke_is_omitted() -> None:
    canvas = Canvas(width=800, height=600)

    canvas.add_shape(
        Circle(
            id="sun",
            center=Point(x=400, y=200),
            radius=100,
            fill=Color(value="#FFD700"),
        )
    )

    root = ET.fromstring(render_svg(canvas))
    circle = root.find(f"{{{SVG_NAMESPACE}}}circle")

    assert circle is not None
    assert "stroke" not in circle.attrib


def test_svg_can_be_written_to_file(tmp_path) -> None:
    canvas = Canvas(width=800, height=600)

    canvas.add_shape(
        Circle(
            id="sun",
            center=Point(x=400, y=200),
            radius=100,
            fill=Color(value="#FFD700"),
        )
    )

    output_path = tmp_path / "painting.svg"

    write_svg(canvas, output_path)

    assert output_path.exists()

    contents = output_path.read_text(encoding="utf-8")
    assert "<circle" in contents
    assert 'id="sun"' in contents
