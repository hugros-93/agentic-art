from painting_agents.domain.session import PaintingSession
from painting_agents.domain.shapes import (
    Circle,
    Color,
    Line,
    Point,
    Rectangle,
)


class CanvasTools:
    def __init__(self, session: PaintingSession) -> None:
        self.session = session

    @property
    def canvas(self):
        return self.session.painting.canvas

    def add_circle(
        self,
        shape_id: str,
        x: float,
        y: float,
        radius: float,
        fill: str,
        stroke: str | None = None,
    ) -> dict:
        circle = Circle(
            id=shape_id,
            center=Point(x=x, y=y),
            radius=radius,
            fill=Color(value=fill),
            stroke=Color(value=stroke) if stroke else None,
        )

        self.canvas.add_shape(circle)

        self.session.record_operation(
            agent_id="unknown",
            operation="add_circle",
            details={"shape_id": shape_id},
        )

        return {
            "success": True,
            "shape": circle.model_dump(),
        }

    def add_rectangle(
        self,
        shape_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str,
        stroke: str | None = None,
    ) -> dict:
        rectangle = Rectangle(
            id=shape_id,
            position=Point(x=x, y=y),
            width=width,
            height=height,
            fill=Color(value=fill),
            stroke=Color(value=stroke) if stroke else None,
        )

        self.canvas.add_shape(rectangle)

        self.session.record_operation(
            agent_id="unknown",
            operation="add_rectangle",
            details={"shape_id": shape_id},
        )

        return {
            "success": True,
            "shape": rectangle.model_dump(),
        }

    def add_line(
        self,
        shape_id: str,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        stroke: str,
        stroke_width: float = 1.0,
    ) -> dict:
        line = Line(
            id=shape_id,
            start=Point(x=start_x, y=start_y),
            end=Point(x=end_x, y=end_y),
            stroke=Color(value=stroke),
            stroke_width=stroke_width,
        )

        self.canvas.add_shape(line)

        self.session.record_operation(
            agent_id="unknown",
            operation="add_line",
            details={"shape_id": shape_id},
        )

        return {
            "success": True,
            "shape": line.model_dump(),
        }

    def remove_shape(self, shape_id: str) -> dict:
        self.canvas.remove_shape(shape_id)

        self.session.record_operation(
            agent_id="unknown",
            operation="remove_shape",
            details={"shape_id": shape_id},
        )

        return {
            "success": True,
            "shape_id": shape_id,
        }

    def get_canvas(self) -> dict:
        return self.canvas.model_dump()