from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from langchain_core.messages import AIMessage

from painting_agents.observability.llm import record_llm_response


def test_record_llm_response_records_usage() -> None:
    exporter = InMemorySpanExporter()

    provider = TracerProvider()
    provider.add_span_processor(
        SimpleSpanProcessor(exporter)
    )

    tracer = provider.get_tracer("test")

    response = AIMessage(
        content="Hello",
        response_metadata={
            "model": "qwen3:0.6b",
            "model_provider": "ollama",
            "done_reason": "stop",
            "total_duration": 6_700_000_000,
            "load_duration": 4_400_000_000,
            "prompt_eval_duration": 140_000_000,
            "eval_duration": 2_000_000_000,
        },
        usage_metadata={
            "input_tokens": 16,
            "output_tokens": 153,
            "total_tokens": 169,
        },
    )

    with tracer.start_as_current_span("llm.call") as span:
        record_llm_response(span, response)

    spans = exporter.get_finished_spans()

    assert len(spans) == 1

    attributes = spans[0].attributes
    assert attributes is not None

    assert attributes["llm.model"] == "qwen3:0.6b"
    assert attributes["llm.provider"] == "ollama"
    assert attributes["llm.input_tokens"] == 16
    assert attributes["llm.output_tokens"] == 153
    assert attributes["llm.total_tokens"] == 169
    assert attributes["llm.total_duration_ms"] == 6700
    assert attributes["llm.load_duration_ms"] == 4400