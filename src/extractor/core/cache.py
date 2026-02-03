"""Sistema de cache com Redis."""

import hashlib
import json
from typing import Any, cast

import redis.asyncio as redis
from pydantic import BaseModel

from extractor.config import Settings, get_settings
from extractor.utils.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Serviço de cache com Redis."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Inicializa conexão Redis."""
        self.settings = settings or get_settings()
        self._redis: redis.Redis[str] | None = None

    async def connect(self) -> None:
        """Conecta ao Redis."""
        if self.settings.cache_enabled:
            self._redis = redis.from_url(
                str(self.settings.redis_url),
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("redis_connected", url=str(self.settings.redis_url))

    async def disconnect(self) -> None:
        """Desconecta do Redis."""
        if self._redis:
            await self._redis.aclose()
            logger.info("redis_disconnected")

    def _generate_key(self, text: str, schema_name: str) -> str:
        """Gera chave de cache baseada no texto e schema."""
        content = f"{schema_name}:{text}"
        return f"extract:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

    async def get(self, text: str, schema_name: str) -> dict[str, Any] | None:
        """Busca resultado em cache."""
        if not self._redis or not self.settings.cache_enabled:
            return None

        key = self._generate_key(text, schema_name)

        try:
            cached = await self._redis.get(key)
            if cached:
                logger.info("cache_hit", key=key)
                return cast(dict[str, Any], json.loads(cached))
        except redis.RedisError as e:
            logger.warning("cache_get_error", error=str(e))

        return None

    async def set(
        self,
        text: str,
        schema_name: str,
        result: BaseModel,
    ) -> None:
        """Armazena resultado em cache."""
        if not self._redis or not self.settings.cache_enabled:
            return

        key = self._generate_key(text, schema_name)

        try:
            await self._redis.setex(
                key,
                self.settings.cache_ttl_seconds,
                result.model_dump_json(),
            )
            logger.info("cache_set", key=key, ttl=self.settings.cache_ttl_seconds)
        except redis.RedisError as e:
            logger.warning("cache_set_error", error=str(e))

    async def delete(self, text: str, schema_name: str) -> bool:
        """Remove item do cache."""
        if not self._redis or not self.settings.cache_enabled:
            return False

        key = self._generate_key(text, schema_name)

        try:
            deleted = await self._redis.delete(key)
            if deleted:
                logger.info("cache_deleted", key=key)
            return bool(deleted)
        except redis.RedisError as e:
            logger.warning("cache_delete_error", error=str(e))
            return False

    async def clear_all(self) -> int:
        """Limpa todo o cache de extração."""
        if not self._redis or not self.settings.cache_enabled:
            return 0

        try:
            keys = []
            async for key in self._redis.scan_iter(match="extract:*"):
                keys.append(key)

            if keys:
                deleted = await self._redis.delete(*keys)
                logger.info("cache_cleared", count=deleted)
                return int(deleted)
            return 0
        except redis.RedisError as e:
            logger.warning("cache_clear_error", error=str(e))
            return 0

    async def health_check(self) -> bool:
        """Verifica se Redis está acessível."""
        if not self._redis:
            return False

        try:
            await self._redis.ping()
            return True
        except redis.RedisError:
            return False
