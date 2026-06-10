import logging

from django.core.cache import caches

from .models import UserAccount

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями"""

    CACHE_TTL = 300  # 5 минут
    CACHE_KEY_PREFIX = "user:"

    @classmethod
    def _get_cache_key(cls: type["UserService"], user_id: int) -> str:
        """Ключ кэша для пользователя"""
        return f"{cls.CACHE_KEY_PREFIX}{user_id}"

    @classmethod
    def get_cached_user(cls: type["UserService"], user_id: int) -> UserAccount:
        """Получить пользователя из кэша или БД"""
        cache = caches["default"]
        cache_key = cls._get_cache_key(user_id)

        # Пробуем кэш
        user = cache.get(cache_key)
        if user:
            logger.info("[CACHE] user_id=%s", user_id)
            return user

        logger.info("[DB] user_id=%s", user_id)
        # Запрос в БД
        user = UserAccount.objects.select_related("role").get(user_id=user_id)

        # Сохраняем в кэш
        cache.set(cache_key, user, cls.CACHE_TTL)

        return user

    @classmethod
    def invalidate_cache(cls: type["UserService"], user_id: int) -> None:
        """Очистить кэш пользователя"""
        cache = caches["default"]
        cache.delete(cls._get_cache_key(user_id))

    @classmethod
    def is_user_active(cls: type["UserService"], user: UserAccount) -> bool:
        """Проверить активность пользователя"""
        return user.is_active


class SystemSettingCacheService:
    """Сервис для кэширования системных настроек"""

    CACHE_TTL = 86400  # 1 день
    CACHE_KEY_MONITORING_YEARS = "system_setting:monitoring_years"

    @classmethod
    def get_monitoring_years(cls: type["SystemSettingCacheService"]) -> str:
        """Получить период мониторинга из кэша"""
        cache = caches["default"]
        data = cache.get(cls.CACHE_KEY_MONITORING_YEARS)
        if data:
            logger.info("[CACHE] monitoring_years hit")
        return data

    @classmethod
    def set_monitoring_years(cls: type["SystemSettingCacheService"], value: str) -> None:
        """Сохранить период мониторинга в кэш"""
        cache = caches["default"]
        cache.set(cls.CACHE_KEY_MONITORING_YEARS, value, cls.CACHE_TTL)
        logger.info("[CACHE] monitoring_years set (ttl=%ss)", cls.CACHE_TTL)

    @classmethod
    def invalidate_monitoring_years(cls: type["SystemSettingCacheService"]) -> None:
        """Очистить кэш периода мониторинга"""
        cache = caches["default"]
        cache.delete(cls.CACHE_KEY_MONITORING_YEARS)
        logger.info("[CACHE] monitoring_years invalidated")
