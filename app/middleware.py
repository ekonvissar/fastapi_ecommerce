from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.config import APP_ENV
from app.logging import request_logging_middleware


async def error_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "-")
    with logger.contextualize(request_id=request_id):
        logger.exception(
            f"Unhandled error on {request.method} {request.url.path}: {exc}"
        )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    if APP_ENV != "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://localhost:8000", "https://127.0.0.1", "null"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.middleware("http")(security_headers_middleware)
    app.middleware("http")(request_logging_middleware)

    app.exception_handler(Exception)(error_handler)
