import pytest
from pydantic import ValidationError

from painting_agents.domain.shapes import (
    Circle,
    Color,
    Line,
    Point,
    Rectangle,
)


def test_point_can_be_created() -> None:
    point = Point(x=100, y=200)

    assert point.x == 100
    assert point.y == 200


def test_color_can_be_created() -> None:
    color = Color(value="#FF0000")

    assert color.value == "#FF0000"


def test_circle_can_be_created() -> None:
    circle = Circle(
        id="sun",
        center=Point(x=500, y=200),
        radius=100,
        fill=Color(value="#FFAA33"),
    )

    assert circle.id == "sun"
    assert circle.type == "circle"
    assert circle.center.x == 500
    assert circle.center.y == 200
    assert circle.radius == 100
    assert circle.fill.value == "#FFAA33"
    assert circle.stroke is None


def test_circle_can_have_stroke() -> None:
    circle = Circle(
        id="sun",
        center=Point(x=500, y=200),
        radius=100,
        fill=Color(value="#FFAA33"),
        stroke=Color(value="#000000"),
    )

    assert circle.stroke is not None
    assert circle.stroke.value == "#000000"


def test_circle_rejects_non_positive_radius() -> None:
    with pytest.raises(ValidationError):
        Circle(
            id="invalid",
            center=Point(x=100, y=100),
            radius=0,
            fill=Color(value="#FF0000"),
        )

    with pytest.raises(ValidationError):
        Circle(
            id="invalid",
            center=Point(x=100, y=100),
            radius=-10,
            fill=Color(value="#FF0000"),
        )


def test_rectangle_can_be_created() -> None:
    rectangle = Rectangle(
        id="sky",
        position=Point(x=0, y=0),
        width=1024,
        height=500,
        fill=Color(value="#87CEEB"),
    )

    assert rectangle.id == "sky"
    assert rectangle.type == "rectangle"
    assert rectangle.position.x == 0
    assert rectangle.position.y == 0
    assert rectangle.width == 1024
    assert rectangle.height == 500
    assert rectangle.fill.value == "#87CEEB"


def test_rectangle_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValidationError):
        Rectangle(
            id="invalid",
            position=Point(x=0, y=0),
            width=0,
            height=100,
            fill=Color(value="#FFFFFF"),
        )

    with pytest.raises(ValidationError):
        Rectangle(
            id="invalid",
            position=Point(x=0, y=0),
            width=100,
            height=-1,
            fill=Color(value="#FFFFFF"),
        )


def test_line_can_be_created() -> None:
    line = Line(
        id="horizon",
        start=Point(x=0, y=500),
        end=Point(x=1024, y=500),
        stroke=Color(value="#000000"),
    )

    assert line.id == "horizon"
    assert line.type == "line"
    assert line.start.x == 0
    assert line.start.y == 500
    assert line.end.x == 1024
    assert line.end.y == 500
    assert line.stroke.value == "#000000"
    assert line.stroke_width == 1.0


def test_line_can_have_custom_stroke_width() -> None:
    line = Line(
        id="horizon",
        start=Point(x=0, y=500),
        end=Point(x=1024, y=500),
        stroke=Color(value="#000000"),
        stroke_width=5,
    )

    assert line.stroke_width == 5


def test_line_rejects_non_positive_stroke_width() -> None:
    with pytest.raises(ValidationError):
        Line(
            id="invalid",
            start=Point(x=0, y=0),
            end=Point(x=100, y=100),
            stroke=Color(value="#000000"),
            stroke_width=0,
        )
