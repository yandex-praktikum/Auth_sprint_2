import uuid

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from api import router as v1_router
from core.config import settings

from fastapi_pagination import add_pagination
from helpers.lifespan import lifespan

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        request_id = str(uuid.uuid4()).encode('utf-8')
        request = Request(request.scope, request.receive)
        request.scope["headers"] = [(k, v) for k, v in request.scope["headers"] if k != b"x-request-id"]
        request.scope["headers"].append((b"x-request-id", request_id))

    with tracer.start_as_current_span("movies_request") as span:
        span.set_attribute("http.request_id", request_id)
        response = await call_next(request)
        return response


FastAPIInstrumentor.instrument_app(app)

add_pagination(app)
app.include_router(v1_router, prefix='/api')
