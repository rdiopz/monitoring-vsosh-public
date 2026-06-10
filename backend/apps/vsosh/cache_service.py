import logging

from django.core.cache import caches

logger = logging.getLogger(__name__)


class VSOSHCacheService:
    """Сервис для кэширования и инвалидации фильтров веб-системы"""

    CACHE_TTL = 300  # 5 минут
    CACHE_KEY_FILTERS = "vsosh_filters"

    @classmethod
    def get_cache(cls):
        """Получить кэш по умолчанию"""
        return caches["default"]

    @classmethod
    def get_filters(cls):
        """Получить данные фильтров из кэша"""
        cache = cls.get_cache()
        data = cache.get(cls.CACHE_KEY_FILTERS)
        if data:
            logger.info("[CACHE] filters hit")
        return data

    @classmethod
    def set_filters(cls, data: dict) -> None:
        """Сохранить данные фильтров в кэш"""
        cache = cls.get_cache()
        cache.set(cls.CACHE_KEY_FILTERS, data, cls.CACHE_TTL)
        logger.info("[CACHE] filters set (ttl=%ss)", cls.CACHE_TTL)

    @classmethod
    def invalidate_filters(cls) -> None:
        """Очистить кэш фильтров"""
        cache = cls.get_cache()
        cache.delete(cls.CACHE_KEY_FILTERS)
        logger.info("[CACHE] filters invalidated")
