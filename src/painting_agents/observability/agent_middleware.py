from __future__ import annotations

from typing import Any

from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
    ToolCallRequest,
)
from langchain_core.messages import AIMessage
from opentelemetry import trace

from painting_agents.observability.llm import (
    record_llm_prompt,
    record_llm_response,
)

class OpenTelemetryAgentMiddleware(AgentMiddleware):
    """OpenTelemetry instrumentation for LangChain agents."""
    def __init__(
        self,
        tracer: trace.Tracer | None = None,
    ) -> None:
        self.tracer = tracer or trace.get_tracer(__name__)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Any,
    ) -> ModelResponse:
        with self.tracer.start_as_current_span("llm.call") as span:
            span.set_attribute("llm.source", "langchain.agent")

            model_name = getattr(request.model, "model", None)
            if isinstance(model_name, str):
                span.set_attribute("llm.model", model_name)

            record_llm_prompt(span, request.messages)

            try:
                response = await handler(request)

                for message in reversed(response.result):
                    if isinstance(message, AIMessage):
                        record_llm_response(span, message)
                        break

                return response

            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR)
                raise

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Any,
    ) -> Any:
        tool = request.tool
        tool_name = tool.name if tool is not None else "unknown"

        with self.tracer.start_as_current_span(
            f"agent.tool.{tool_name}"
        ) as span:
            span.set_attribute(
                "tool.name",
                tool_name,
            )

            span.add_event(
                "tool.input",
                {
                    "input": str(request.tool_call),
                },
            )

            try:
                result = await handler(request)

                span.add_event(
                    "tool.output",
                    {
                        "output": str(result),
                    },
                )

                return result
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(trace.StatusCode.ERROR)
                raise

    @staticmethod
    def _record_response(
        span: trace.Span,
        response: ModelResponse,
    ) -> None:
        for message in reversed(response.result):
            if isinstance(message, AIMessage):
                record_llm_response(
                    span,
                    message,
                )
                return