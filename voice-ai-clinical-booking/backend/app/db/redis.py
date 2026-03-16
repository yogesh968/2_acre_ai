import redis.asyncio as redis
from app.core.config import get_settings
import json
from typing import Optional, Any

settings = get_settings()

class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        if not self.redis:
            return None
        data = await self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None
    
    async def set_session(self, session_id: str, data: dict, ttl: int = None):
        if not self.redis:
            return
        ttl = ttl or settings.REDIS_SESSION_TTL
        await self.redis.setex(
            f"session:{session_id}",
            ttl,
            json.dumps(data)
        )
    
    async def delete_session(self, session_id: str):
        if not self.redis:
            return
        await self.redis.delete(f"session:{session_id}")
    
    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            return None
        return await self.redis.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None):
        if not self.redis:
            return
        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

redis_client = RedisClient()
