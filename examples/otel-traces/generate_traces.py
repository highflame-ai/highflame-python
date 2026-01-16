import os
from typing import Any, Dict

from openai import OpenAI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracer() -> trace.Tracer:
    """Configure an OTLP exporter that talks directly to the collector."""
    resource = Resource.create(
        {
            "service.name": os.getenv("OTEL_SERVICE_NAME", "trace-generator"),
            "service.namespace": "javelin-cerberus",
        }
    )
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTLP_ENDPOINT")
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(__name__)


tracer = init_tracer()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def record_completion_attributes(span: trace.Span, usage: Any) -> None:
    if not usage:
        return

    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value: Any = getattr(usage, key, None)
        if value is None and isinstance(usage, Dict):
            value = usage.get(key)
        if value is not None:
            span.set_attribute(f"llm.usage.{key}", value)


def generate_trace() -> None:
    with tracer.start_as_current_span("openai.chat.completions.create") as span:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a very accurate calculator. Output only the result.",
                },
                {"role": "user", "content": "1 + 1 = "},
            ],
            metadata={"someMetadataKey": "someValue"},
        )

        span.set_attribute("llm.model", "gpt-4o")
        span.set_attribute("prompt.user_question", "1 + 1 = ")
        span.set_attribute("response.id", completion.id)
        record_completion_attributes(span, getattr(completion, "usage", {}) or {})

        answer = completion.choices[0].message.content
        span.set_attribute("response.preview", answer)
        span.set_attribute("input", "1 + 1 = ")
        span.set_attribute("output", answer)
        print(answer)


if __name__ == "__main__":
    generate_trace()