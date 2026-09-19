from typing import Literal

from pydantic import BaseModel, Field


class Point(BaseModel):
    x: float
    y: float


class Color(BaseModel):
    value: str


class Circle(BaseModel):
    id: str
    type: Literal["circle"] = "circle"
    center: Point
    radius: float = Field(gt=0)
    fill: Color
    stroke: Color | None = None


class Rectangle(BaseModel):
    id: str
    type: Literal["rectangle"] = "rectangle"
    position: Point
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    fill: Color
    stroke: Color | None = None


class Line(BaseModel):
    id: str
    type: Literal["line"] = "line"
    start: Point
    end: Point
    stroke: Color
    stroke_width: float = Field(default=1.0, gt=0)


Shape = Circle | Rectangle | Line