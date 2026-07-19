"""Redis-backed token store for refresh tokens and access denylist."""

from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis


class RedisTokenStore:
    """Store revocable token state in Redis."""

    def __init__(self, redis: Redis, *, key_prefix: str = "sarathi:auth") -> None:
        self._redis = redis
        self._prefix = key_prefix

    def _refresh_key(self, jti: str) -> str:
        return f"{self._prefix}:refresh:{jti}"

    def _user_refresh_set_key(self, user_id: UUID) -> str:
        return f"{self._prefix}:user_refresh:{user_id}"

    def _denylist_key(self, jti: str) -> str:
        return f"{self._prefix}:denylist:{jti}"

    @staticmethod
    def _ttl_seconds(expires_at: datetime) -> int:
        now = datetime.now(UTC)
        aware = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=UTC)
        return max(int((aware - now).total_seconds()), 1)

    async def store_refresh_token(
        self,
        *,
        jti: str,
        user_id: UUID,
        expires_at: datetime,
    ) -> None:
        """Persist an active refresh token until expiry."""
        ttl = self._ttl_seconds(expires_at)
        refresh_key = self._refresh_key(jti)
        user_set_key = self._user_refresh_set_key(user_id)
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.set(refresh_key, str(user_id), ex=ttl)
            pipe.sadd(user_set_key, jti)
            pipe.expire(user_set_key, ttl)
            await pipe.execute()

    async def get_refresh_user_id(self, jti: str) -> UUID | None:
        """Return the user id for an active refresh token, if present."""
        value = await self._redis.get(self._refresh_key(jti))
        if value is None:
            return None
        return UUID(str(value))

    async def revoke_refresh_token(self, jti: str) -> None:
        """Revoke a refresh token immediately."""
        refresh_key = self._refresh_key(jti)
        user_id = await self._redis.get(refresh_key)
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.delete(refresh_key)
            if user_id is not None:
                pipe.srem(self._user_refresh_set_key(UUID(str(user_id))), jti)
            await pipe.execute()

    async def revoke_all_refresh_tokens_for_user(self, user_id: UUID) -> None:
        """Revoke every refresh token belonging to a user."""
        user_set_key = self._user_refresh_set_key(user_id)
        jtis = await self._redis.smembers(user_set_key)
        if not jtis:
            return
        async with self._redis.pipeline(transaction=True) as pipe:
            for jti in jtis:
                pipe.delete(self._refresh_key(str(jti)))
            pipe.delete(user_set_key)
            await pipe.execute()

    async def denylist_access_token(self, *, jti: str, expires_at: datetime) -> None:
        """Add an access-token jti to the denylist until it expires."""
        ttl = self._ttl_seconds(expires_at)
        await self._redis.set(self._denylist_key(jti), "1", ex=ttl)

    async def is_access_token_denylisted(self, jti: str) -> bool:
        """Return True if the access-token jti has been revoked."""
        return bool(await self._redis.exists(self._denylist_key(jti)))
