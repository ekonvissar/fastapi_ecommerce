from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.lifespan import lifespan
from app.logging import setup_logging
from app.middleware import setup_middleware
from app.router_loader import include_routers
from app.shared.exception_handlers import register_exception_handlers

MEDIA_DIR = Path("media")
STATIC_DIR = Path("static")


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="FastAPI интеренет-магазин",
        version="0.1.0",
        lifespan=lifespan,
    )

    setup_middleware(app)
    register_exception_handlers(app)
    include_routers(app)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app
