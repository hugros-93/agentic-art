import json
from typing import Any


def parse_mcp_result(result: Any) -> dict[str, Any]:
    """Convert an MCP tool result into a Python dictionary."""
    if isinstance(result, dict):
        return result

    if not isinstance(result, list):
        raise TypeError(
            f"Unexpected MCP result type: {type(result).__name__}"
        )

    for item in result:
        if not isinstance(item, dict):
            continue

        text = item.get("text")
        if not isinstance(text, str):
            continue

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            return parsed

    raise ValueError(f"Could not parse MCP tool result: {result!r}")