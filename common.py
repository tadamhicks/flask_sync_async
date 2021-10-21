import os
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import trace
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    BatchSpanProcessor
)
from grpc import ssl_channel_credentials

def otel_init():

    resource = Resource(attributes={
    "service.name": 'celery'
    })

    trace_provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(
        endpoint="api.honeycomb.io:443",
        insecure=False,
        credentials=ssl_channel_credentials(),
        headers=(
            ("x-honeycomb-team", os.environ['HONEYCOMB_API_KEY']),
            ("x-honeycomb-dataset", 'celery')
        )
    )

    trace_provider.add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )
    trace.set_tracer_provider(trace_provider)
    CeleryInstrumentor().instrument()
