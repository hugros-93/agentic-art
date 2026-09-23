from pydantic import BaseModel

from .canvas import Canvas


class Painting(BaseModel):
    id: str
    title: str
    canvas: Canvas
