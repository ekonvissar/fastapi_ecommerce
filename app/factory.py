from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.logging import setup_logging
from app.middleware import setup_middleware
from app.router_loader import include_routers

MEDIA_DIR = Path("media")
STATIC_DIR = Path("static")


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="FastAPI интеренет-магазин",
        version="0.1.0",
    )

    setup_middleware(app)
    include_routers(app)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app
