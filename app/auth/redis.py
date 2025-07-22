# app/auth/redis.py
from app.core.config import get_settings

try:
    import aioredis  # type: ignore
except Exception:  # pragma: no cover - optional dependency may not be available
    aioredis = None

settings = get_settings()

async def get_redis():
    if aioredis is None:
        raise RuntimeError("aioredis is required for Redis functionality")
    if not hasattr(get_redis, "redis"):
        get_redis.redis = await aioredis.from_url(
            settings.REDIS_URL or "redis://localhost"
        )
    return get_redis.redis

async def add_to_blacklist(jti: str, exp: int):
    """Add a token's JTI to the blacklist"""
    if aioredis is None:
        return
    redis = await get_redis()
    await redis.set(f"blacklist:{jti}", "1", ex=exp)

async def is_blacklisted(jti: str) -> bool:
    """Check if a token's JTI is blacklisted"""
    if aioredis is None:
        return False
    redis = await get_redis()
    return await redis.exists(f"blacklist:{jti}")