from time import time
from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse


async def log_request_middleware(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    duration = time() - start_time
    print(f"{request.method} {request.url.path} completed in {duration:.2f} seconds")
    return response


async def error_handler(request: Request, exc: Exception):
    print(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response