import pytest

from painting_agents.mcp.results import parse_mcp_result


def test_parse_dict_result() -> None:
    result = {"success": True, "shape_id": "sun"}

    assert parse_mcp_result(result) == result


def test_parse_mcp_text_result() -> None:
    result = [
        {
            "type": "text",
            "text": '{"success": true, "shape_id": "sun"}',
            "id": "test-id",
        }
    ]

    assert parse_mcp_result(result) == {
        "success": True,
        "shape_id": "sun",
    }


def test_parse_mcp_result_skips_non_json_items() -> None:
    result = [
        {"type": "image"},
        {"type": "text", "text": "not json"},
        {
            "type": "text",
            "text": '{"success": true}',
        },
    ]

    assert parse_mcp_result(result) == {"success": True}


def test_parse_mcp_result_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="Could not parse MCP tool result"):
        parse_mcp_result([{"type": "image"}])


def test_parse_mcp_result_rejects_unknown_type() -> None:
    with pytest.raises(TypeError, match="Unexpected MCP result type"):
        parse_mcp_result("not an MCP result")
