from __future__ import annotations

from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from opentelemetry import trace

from painting_agents.observability.llm import (
    record_llm_prompt,
    record_llm_response,
)

tracer = trace.get_tracer(__name__)


class OpenTelemetryCallbackHandler(BaseCallbackHandler):
    """Bridge LangChain model/tool lifecycle events into OpenTelemetry."""

    def __init__(self) -> None:
        self._spans: dict[str, trace.Span] = {}

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: Any,
        **kwargs: Any,
    ) -> Any:
        span = tracer.start_span("llm.call")

        span.set_attribute("llm.source", "langchain")

        if serialized:
            name = serialized.get("name")
            if isinstance(name, str):
                span.set_attribute("llm.class", name)

        flattened = [
            message
            for message_group in messages
            for message in message_group
        ]

        record_llm_prompt(span, flattened)

        self._spans[str(run_id)] = span

    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: Any,
        **kwargs: Any,
    ) -> Any:
        span = self._spans.pop(str(run_id), None)

        if span is None:
            return

        try:
            message = response.generations[0][0].message

            if hasattr(message, "usage_metadata"):
                record_llm_response(span, message)
        finally:
            span.end()

    def on_chat_model_end(
        self,
        response: Any,
        *,
        run_id: Any,
        **kwargs: Any,
    ) -> Any:
        span = self._spans.pop(str(run_id), None)

        if span is None:
            return

        try:
            message = response.generations[0][0].message

            if hasattr(message, "usage_metadata"):
                record_llm_response(span, message)
        finally:
            span.end()

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: Any,
        **kwargs: Any,
    ) -> Any:
        span = self._spans.pop(str(run_id), None)

        if span is None:
            return

        span.record_exception(error)
        span.set_status(trace.StatusCode.ERROR)
        span.end()