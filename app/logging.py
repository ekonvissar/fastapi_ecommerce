import sys
from time import time
from uuid import uuid4

from fastapi import Request
from loguru import logger
from starlette.responses import JSONResponse


def setup_logging() -> None:
    logger.remove()
    logger.configure(extra={"request_id": "-"})
    logger.add(
        sys.stderr,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
            "{extra[request_id]} | {message}"
        ),
        level="INFO",
    )


async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    start_time = time()

    with logger.contextualize(request_id=request_id):
        try:
            response = await call_next(request)
            duration = time() - start_time
            response.headers["X-Request-Id"] = request_id

            message = (
                f"{request.method} {request.url.path} "
                f"{response.status_code} {duration:.3f}s"
            )
            if response.status_code >= 500:
                logger.error(message)
            elif response.status_code in (401, 403):
                logger.warning(message)
            else:
                logger.info(message)

            return response
        except Exception:
            duration = time() - start_time
            logger.exception(
                f"{request.method} {request.url.path} failed after {duration:.3f}s"
            )
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
            response.headers["X-Request-Id"] = request_id
            return response
