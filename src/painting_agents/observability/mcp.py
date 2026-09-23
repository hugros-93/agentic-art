from __future__ import annotations

from typing import Any

from opentelemetry import trace


def record_mcp_result(
    span: trace.Span,
    result: Any,
) -> None:
    if not isinstance(result, dict):
        return

    success = result.get("success")
    if isinstance(success, bool):
        span.set_attribute("mcp.success", success)

    shape = result.get("shape")
    if isinstance(shape, dict):
        shape_id = shape.get("id")
        shape_type = shape.get("type")

        if isinstance(shape_id, str):
            span.set_attribute("painting.shape_id", shape_id)

        if isinstance(shape_type, str):
            span.set_attribute("painting.shape_type", shape_type)
