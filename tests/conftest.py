import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth import create_access_token
from app.config import get_settings
from app.db.deps import get_async_db, get_redis
from app.main import app
from app.models.cart_items import CartItem
from app.models.categories import Category
from app.models.users import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class FakeRedis:
    def __init__(self):
        self._store: dict[str, str] = {}

    async def set(self, key, value, ex=None):
        self._store[key] = value
        return True

    async def delete(self, key):
        if key in self._store:
            del self._store[key]
            return 1
        return 0

    async def scan_iter(self, match=None):
        if match and match.endswith("*"):
            prefix = match[:-1]
            for key in list(self._store):
                if key.startswith(prefix):
                    yield key


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA foreign_keys=OFF"))
        await conn.run_sync(Category.__table__.create)
        await conn.run_sync(User.__table__.create)
        await conn.run_sync(CartItem.__table__.create)

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_async_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_async_db] = override_get_async_db

    fake_redis = FakeRedis()

    async def override_get_redis():
        yield fake_redis

    app.dependency_overrides[get_redis] = override_get_redis

    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client

    app.dependency_overrides.clear()
    await engine.dispose()


def register_user(client, email="buyer@test.com", password="password123", role="buyer"):
    return client.post(
        "/users/",
        json={"email": email, "password": password, "role": role},
    )


def auth_headers(email: str, user_id: int, role: str = "buyer") -> dict:
    token = create_access_token(
        {"sub": email, "role": role, "id": user_id}, get_settings()
    )
    return {"Authorization": f"Bearer {token}"}


def login_user(client, email="buyer@test.com", password="password123"):
    return client.post(
        "/users/token",
        data={"username": email, "password": password},
    )


def create_category(client, name="Phones", parent_id=None):
    return client.post(
        "/categories/",
        json={"name": name, "parent_id": parent_id},
    )
