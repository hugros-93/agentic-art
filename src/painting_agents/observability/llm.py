from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from opentelemetry import trace


def record_llm_response(
    span: trace.Span,
    response: AIMessage,
) -> None:
    usage = response.usage_metadata or {}
    metadata = response.response_metadata or {}

    _set_attribute(span, "llm.input_tokens", usage.get("input_tokens"))
    _set_attribute(span, "llm.output_tokens", usage.get("output_tokens"))
    _set_attribute(span, "llm.total_tokens", usage.get("total_tokens"))

    model = metadata.get("model") or metadata.get("model_name")
    _set_attribute(span, "llm.model", model)
    _set_attribute(span, "llm.provider", metadata.get("model_provider"))
    _set_attribute(span, "llm.finish_reason", metadata.get("done_reason"))

    _set_duration_ms(
        span,
        "llm.total_duration_ms",
        metadata.get("total_duration"),
    )

    _set_duration_ms(
        span,
        "llm.load_duration_ms",
        metadata.get("load_duration"),
    )

    _set_duration_ms(
        span,
        "llm.prompt_eval_duration_ms",
        metadata.get("prompt_eval_duration"),
    )

    _set_duration_ms(
        span,
        "llm.eval_duration_ms",
        metadata.get("eval_duration"),
    )

    if response.content:
        span.add_event(
            "llm.response",
            {"content": str(response.content)},
        )

def record_llm_prompt(
    span: trace.Span,
    messages: Sequence[BaseMessage],
) -> None:
    """Record the application-level prompt as an OpenTelemetry event."""

    for index, message in enumerate(messages):
        content = message.content

        span.add_event(
            "llm.prompt",
            {
                "message.index": index,
                "message.type": message.type,
                "content": str(content),
            },
        )


def _set_attribute(
    span: trace.Span,
    name: str,
    value: Any,
) -> None:
    if value is not None:
        span.set_attribute(name, value)


def _set_duration_ms(
    span: trace.Span,
    name: str,
    nanoseconds: Any,
) -> None:
    if isinstance(nanoseconds, (int, float)):
        span.set_attribute(name, nanoseconds / 1_000_000)