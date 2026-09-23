from typing import Any

from opentelemetry import trace

from painting_agents.domain.session import PaintingSession
from painting_agents.domain.shapes import (
    Circle,
    Color,
    Line,
    Point,
    Rectangle,
)
from painting_agents.observability.mcp import record_mcp_result


class CanvasTools:
    def __init__(
        self,
        session: PaintingSession,
        *,
        agent_id: str = "unknown",
        tracer: trace.Tracer | None = None,
    ) -> None:
        self.session = session
        self.agent_id = agent_id
        self.tracer = tracer or trace.get_tracer(__name__)

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
    ) -> dict[str, Any]:
        with self.tracer.start_as_current_span("mcp.add_circle") as span:
            span.set_attribute("mcp.tool", "add_circle")
            span.set_attribute("painting.agent_id", self.agent_id)
            span.set_attribute("painting.shape_id", shape_id)
            span.set_attribute("painting.x", x)
            span.set_attribute("painting.y", y)
            span.set_attribute("painting.radius", radius)
            span.set_attribute("painting.fill", fill)

            if stroke is not None:
                span.set_attribute("painting.stroke", stroke)

            try:
                circle = Circle(
                    id=shape_id,
                    center=Point(x=x, y=y),
                    radius=radius,
                    fill=Color(value=fill),
                    stroke=Color(value=stroke) if stroke else None,
                )

                self.canvas.add_shape(circle)

                self.session.record_operation(
                    agent_id=self.agent_id,
                    operation="add_circle",
                    details={
                        "shape_id": shape_id,
                        "x": x,
                        "y": y,
                        "radius": radius,
                        "fill": fill,
                        "stroke": stroke,
                    },
                )

                result = {
                    "success": True,
                    "shape": circle.model_dump(),
                }

                record_mcp_result(span, result)
                return result

            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR)
                raise

    def add_rectangle(
        self,
        shape_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str,
        stroke: str | None = None,
    ) -> dict[str, Any]:
        with self.tracer.start_as_current_span("mcp.add_rectangle") as span:
            span.set_attribute("mcp.tool", "add_rectangle")
            span.set_attribute("painting.agent_id", self.agent_id)
            span.set_attribute("painting.shape_id", shape_id)
            span.set_attribute("painting.x", x)
            span.set_attribute("painting.y", y)
            span.set_attribute("painting.width", width)
            span.set_attribute("painting.height", height)
            span.set_attribute("painting.fill", fill)

            if stroke is not None:
                span.set_attribute("painting.stroke", stroke)

            try:
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
                    agent_id=self.agent_id,
                    operation="add_rectangle",
                    details={
                        "shape_id": shape_id,
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                        "fill": fill,
                        "stroke": stroke,
                    },
                )

                result = {
                    "success": True,
                    "shape": rectangle.model_dump(),
                }

                record_mcp_result(span, result)
                return result

            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR)
                raise

    def add_line(
        self,
        shape_id: str,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        stroke: str,
        stroke_width: float = 1.0,
    ) -> dict[str, Any]:
        with self.tracer.start_as_current_span("mcp.add_line") as span:
            span.set_attribute("mcp.tool", "add_line")
            span.set_attribute("painting.agent_id", self.agent_id)
            span.set_attribute("painting.shape_id", shape_id)
            span.set_attribute("painting.start_x", start_x)
            span.set_attribute("painting.start_y", start_y)
            span.set_attribute("painting.end_x", end_x)
            span.set_attribute("painting.end_y", end_y)
            span.set_attribute("painting.stroke", stroke)
            span.set_attribute("painting.stroke_width", stroke_width)

            try:
                line = Line(
                    id=shape_id,
                    start=Point(x=start_x, y=start_y),
                    end=Point(x=end_x, y=end_y),
                    stroke=Color(value=stroke),
                    stroke_width=stroke_width,
                )

                self.canvas.add_shape(line)

                self.session.record_operation(
                    agent_id=self.agent_id,
                    operation="add_line",
                    details={
                        "shape_id": shape_id,
                        "start_x": start_x,
                        "start_y": start_y,
                        "end_x": end_x,
                        "end_y": end_y,
                        "stroke": stroke,
                        "stroke_width": stroke_width,
                    },
                )

                result = {
                    "success": True,
                    "shape": line.model_dump(),
                }

                record_mcp_result(span, result)
                return result

            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR)
                raise

    def remove_shape(self, shape_id: str) -> dict[str, Any]:
        with self.tracer.start_as_current_span("mcp.remove_shape") as span:
            span.set_attribute("mcp.tool", "remove_shape")
            span.set_attribute("painting.agent_id", self.agent_id)
            span.set_attribute("painting.shape_id", shape_id)

            try:
                self.canvas.remove_shape(shape_id)

                self.session.record_operation(
                    agent_id=self.agent_id,
                    operation="remove_shape",
                    details={
                        "shape_id": shape_id,
                    },
                )

                result = {
                    "success": True,
                    "shape_id": shape_id,
                }

                record_mcp_result(span, result)
                return result

            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR)
                raise

    def get_canvas(self) -> dict[str, Any]:
        with self.tracer.start_as_current_span("mcp.get_canvas") as span:
            span.set_attribute("mcp.tool", "get_canvas")
            span.set_attribute("painting.agent_id", self.agent_id)

            try:
                result = self.canvas.model_dump()

                span.set_attribute(
                    "painting.shape_count",
                    len(self.canvas.shapes),
                )

                record_mcp_result(span, result)
                return result

            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR)
                raise
