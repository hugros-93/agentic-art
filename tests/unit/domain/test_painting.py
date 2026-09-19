from painting_agents.domain.canvas import Canvas
from painting_agents.domain.painting import Painting


def test_painting_can_be_created() -> None:
    canvas = Canvas(width=1024, height=768)

    painting = Painting(
        id="painting-1",
        title="Sunset",
        canvas=canvas,
    )

    assert painting.id == "painting-1"
    assert painting.title == "Sunset"
    assert painting.canvas is canvas