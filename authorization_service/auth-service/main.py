import logging

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse

from src.api import router as v1_router
from src.core.api_settings import settings
from src.core.logger import setup_logging
from src.helpers.lifespan import lifespan

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

setup_logging()

tracer = trace.get_tracer(__name__)

app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description='Auth API endpoints',
    version='1.0.0'
)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    with tracer.start_as_current_span("auth_request") as span:
        span.set_attribute("http.request_id", request_id)
        response = await call_next(request)
        return response


FastAPIInstrumentor.instrument_app(app)

app.include_router(v1_router, prefix="/api")

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001,
    )
