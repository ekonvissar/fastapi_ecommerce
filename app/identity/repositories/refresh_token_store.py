from redis.asyncio import Redis


class RefreshTokenStore:
    """Хранение refresh jti в Redis — только I/O, без JWT-логики."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @staticmethod
    def _key(user_id: int, jti: str) -> str:
        return f"refresh:{user_id}:{jti}"

    async def save(self, user_id: int, jti: str, ttl: int) -> None:
        await self._redis.set(self._key(user_id, jti), str(user_id), ex=ttl)

    async def delete(self, user_id: int, jti: str) -> int:
        return await self._redis.delete(self._key(user_id, jti))

    async def delete_all_for_user(self, user_id: int) -> None:
        async for key in self._redis.scan_iter(f"refresh:{user_id}:*"):
            await self._redis.delete(key)
