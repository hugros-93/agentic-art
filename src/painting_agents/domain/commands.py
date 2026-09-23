from pydantic import BaseModel

from .shapes import Circle, Line, Rectangle


class DrawCircleCommand(BaseModel):
    shape: Circle


class DrawRectangleCommand(BaseModel):
    shape: Rectangle


class DrawLineCommand(BaseModel):
    shape: Line


class DeleteShapeCommand(BaseModel):
    shape_id: str
