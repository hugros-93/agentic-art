from uuid import uuid4

from painting_agents.domain.canvas import Canvas
from painting_agents.domain.painting import Painting
from painting_agents.domain.session import PaintingSession


def create_painting_session(
    *,
    title: str,
    width: int = 1024,
    height: int = 768,
) -> PaintingSession:
    painting = Painting(
        id=str(uuid4()),
        title=title,
        canvas=Canvas(
            width=width,
            height=height,
        ),
    )

    return PaintingSession(
        id=str(uuid4()),
        painting=painting,
    )
