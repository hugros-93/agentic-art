import pytest

from painting_agents.domain.canvas import Canvas
from painting_agents.domain.shapes import Circle, Color, Point


def make_circle(shape_id: str = "circle-1") -> Circle:
    return Circle(
        id=shape_id,
        center=Point(x=100, y=100),
        radius=50,
        fill=Color(value="#FF0000"),
    )


def test_canvas_can_be_created() -> None:
    canvas = Canvas(width=1024, height=768)

    assert canvas.width == 1024
    assert canvas.height == 768
    assert canvas.shapes == []


def test_canvas_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError):
        Canvas(width=0, height=768)

    with pytest.raises(ValueError):
        Canvas(width=1024, height=0)

    with pytest.raises(ValueError):
        Canvas(width=-1, height=768)


def test_shape_can_be_added() -> None:
    canvas = Canvas(width=1024, height=768)
    circle = make_circle()

    canvas.add_shape(circle)

    assert len(canvas.shapes) == 1
    assert canvas.shapes[0] == circle


def test_multiple_shapes_can_be_added() -> None:
    canvas = Canvas(width=1024, height=768)

    first = make_circle("circle-1")
    second = make_circle("circle-2")

    canvas.add_shape(first)
    canvas.add_shape(second)

    assert len(canvas.shapes) == 2
    assert canvas.shapes[0].id == "circle-1"
    assert canvas.shapes[1].id == "circle-2"


def test_duplicate_shape_id_is_rejected() -> None:
    canvas = Canvas(width=1024, height=768)

    canvas.add_shape(make_circle("sun"))

    with pytest.raises(ValueError, match="Shape already exists: sun"):
        canvas.add_shape(make_circle("sun"))


def test_shape_can_be_removed() -> None:
    canvas = Canvas(width=1024, height=768)

    circle = make_circle("sun")
    canvas.add_shape(circle)

    canvas.remove_shape("sun")

    assert canvas.shapes == []


def test_removing_unknown_shape_is_rejected() -> None:
    canvas = Canvas(width=1024, height=768)

    with pytest.raises(ValueError, match="Shape not found: missing"):
        canvas.remove_shape("missing")


def test_removing_one_shape_does_not_remove_others() -> None:
    canvas = Canvas(width=1024, height=768)

    first = make_circle("first")
    second = make_circle("second")

    canvas.add_shape(first)
    canvas.add_shape(second)

    canvas.remove_shape("first")

    assert len(canvas.shapes) == 1
    assert canvas.shapes[0].id == "second"