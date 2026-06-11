from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.database import async_engine
from app.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")
    await async_engine.dispose()
    await redis_client.aclose()
