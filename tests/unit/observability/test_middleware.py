from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain.agents.middleware import ModelRequest, ModelResponse
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from painting_agents.observability.agent_middleware import (
    OpenTelemetryAgentMiddleware,
)

model = MagicMock(spec=BaseChatModel)
model.model = "qwen3:0.6b"

@pytest.mark.asyncio
async def test_model_middleware_records_llm_call() -> None:
    exporter = InMemorySpanExporter()

    provider = TracerProvider()
    provider.add_span_processor(
        SimpleSpanProcessor(exporter)
    )

    middleware = OpenTelemetryAgentMiddleware(
        tracer=provider.get_tracer("test"),
    )

    message = HumanMessage(
        content="Draw a red circle."
    )

    response = ModelResponse(
        result=[
            AIMessage(
                content="I will draw the circle.",
                response_metadata={
                    "model": "qwen3:0.6b",
                    "model_provider": "ollama",
                },
                usage_metadata={
                    "input_tokens": 10,
                    "output_tokens": 7,
                    "total_tokens": 17,
                },
            )
        ]
    )

    handler = AsyncMock(
        return_value=response
    )

    request = ModelRequest(
        model=model,
        messages=[message],
        system_message=None,
        tools=[],
        response_format=None,
        state=None,
        runtime=None,
    )

    result = await middleware.awrap_model_call(
        request,
        handler,
    )

    assert result is response
    handler.assert_awaited_once()

    spans = exporter.get_finished_spans()

    assert len(spans) == 1

    span = spans[0]

    assert span.name == "llm.call"

    attributes = span.attributes
    assert attributes is not None

    assert attributes["llm.source"] == "langchain.agent"
    assert attributes["llm.model"] == "qwen3:0.6b"
    assert attributes["llm.provider"] == "ollama"
    assert attributes["llm.input_tokens"] == 10
    assert attributes["llm.output_tokens"] == 7
    assert attributes["llm.total_tokens"] == 17

    event_names = [
        event.name
        for event in span.events
    ]

    assert "llm.prompt" in event_names
    assert "llm.response" in event_names