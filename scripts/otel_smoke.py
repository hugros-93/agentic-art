import time

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


def main() -> None:
    resource = Resource.create(
        {
            "service.name": "painting-agents-smoke",
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True,
    )

    provider.add_span_processor(SimpleSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer("painting-agents.smoke")

    with tracer.start_as_current_span("smoke.test") as span:
        span.set_attribute(
            "test.message",
            "Hello Jaeger",
        )

        time.sleep(0.2)

    provider.force_flush()

    print("Smoke trace exported.")


if __name__ == "__main__":
    main()
