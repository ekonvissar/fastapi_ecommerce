from collections.abc import AsyncGenerator

from redis.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.redis import redis_client


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_redis() -> AsyncGenerator[Redis, None]:
    yield redis_client
