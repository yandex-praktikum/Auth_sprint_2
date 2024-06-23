from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def configure_tracer(jager_host: str, jager_port: int, service_name: str) -> None:
    """
    Configures Jaeger Tracer
    :param jager_host: Jaeger host
    :param jager_port: Jaeger port
    :param service_name: Service name
    :return: None
    """
    resource = Resource(attributes={SERVICE_NAME: service_name})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=jager_host,
                agent_port=jager_port,
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
