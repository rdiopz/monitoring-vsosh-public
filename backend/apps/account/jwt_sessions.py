import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any

from django.conf import settings
from django.core.cache import caches
from django.utils import timezone
from ipware import get_client_ip
from redis.client import Pipeline, Redis
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import Token
from user_agents import parse
from user_agents.parsers import UserAgent

from .constants import Errors, RevokeReasons
from .models import UserAccount

logger = logging.getLogger(__name__)


class SessionService:
    """Основной класс для работы с JWT-сессиями"""

    def __init__(self):
        """
        Инициализирует сервис сессий.

        Создает композицию из двух основных компонентов:
        - extractor: для извлечения и валидации данных из HTTP-запросов
        - storage: для работы с Redis-хранилищем сессий
        """
        self.extractor = RequestExtractor()
        self.storage = SessionStorage()

    def add_session(self, token: Token, request: Request) -> str:
        """Добавление сессии в Redis хранилище"""
        extracted_data = self.extractor.extract_session_data(token=token, request=request)

        # Проверка: есть ли у пользователя активные сессии с другим fingerprint/ip
        existing_sessions = self.storage.get_user_sessions(
            user_id=extracted_data["user_id"],
            current_jti=extracted_data["jti"],
            active_only=True,
            raw=True,
        )

        if existing_sessions:
            # Проверяем fingerprint
            different_fp = any(
                session.get("fingerprint") != extracted_data["fingerprint"]
                for session in existing_sessions
            )
            if different_fp:
                extracted_data["fingerprint_mismatch"] = True
                logger.warning(
                    f"Подозрительная сессия (fingerprint): user_id={extracted_data['user_id']}, "
                    f"новый fingerprint={extracted_data['fingerprint'][:8]}..., "
                    f"существующие={[session.get('fingerprint', '')[:8] for session in existing_sessions]}"
                )

            # Проверяем IP
            current_ip = extracted_data.get("ip")
            different_ip = any(session.get("ip") != current_ip for session in existing_sessions)
            if different_ip:
                extracted_data["ip_changed"] = True
                extracted_data["new_ip"] = current_ip
                logger.warning(
                    f"Подозрительная сессия (IP): user_id={extracted_data['user_id']}, "
                    f"новый IP={current_ip}, "
                    f"существующие={[session.get('ip', '') for session in existing_sessions]}"
                )

        ttl = token.payload.get("exp", 0) - int(time.time())
        return self.storage.create_session(extracted_data=extracted_data, ttl=ttl)

    def validate_session(self, jti: str, request: Request) -> tuple[bool, str]:
        """Проверить валидность сессии"""
        session = self.storage.get_session(jti)

        if not session:
            return False, Errors.SESSION_NOT_FOUND

        if not session.get("active", False):
            return False, Errors.SESSION_NOT_ACTIVE

        is_valid = self.extractor.validate_fingerprint(session.get("fingerprint"), request)

        if not is_valid and session.get("fingerprint"):
            updates = {
                "fingerprint_mismatch": True,
                "last_mismatch": timezone.now().isoformat(),
            }

            current_ip = self.extractor.get_client_ip(request)
            if session.get("ip_address") and session["ip_address"] != current_ip:
                updates.update({"ip_changed": True, "new_ip": current_ip})

            self.storage.update_session(jti, updates)

            logger.warning(
                f"Несоответствие 'отпечатка' для сеанса {jti}... "
                f"Ожидали: {session['fingerprint']}..., "
                f"Получили: {self.extractor.generate_fingerprint(request)}..."
            )

            return True, Errors.FINGERPRINT_MISMATCH

        return True, Errors.SESSION_ACTIVE


class RequestExtractor:
    """Извлечение информации из HTTP запроса"""

    # Ключи для request.META
    META_USER_AGENT = "HTTP_USER_AGENT"
    META_ACCEPT_LANGUAGE = "HTTP_ACCEPT_LANGUAGE"
    META_ACCEPT_ENCODING = "HTTP_ACCEPT_ENCODING"
    META_ACCEPT_CHARSET = "HTTP_ACCEPT_CHARSET"
    META_X_FORWARDED_FOR = "HTTP_X_FORWARDED_FOR"
    META_REMOTE_ADDR = "REMOTE_ADDR"

    @staticmethod
    @lru_cache(maxsize=128)
    def _parse_user_agent(user_agent: str) -> UserAgent:
        """Кэшированный парсинг UA"""
        return parse(user_agent)

    def get_client_ip(self, request: Request) -> str:
        """Получить IP клиента"""
        ip, _ = get_client_ip(request)
        return ip or ""

    def analyze_user_agent(self, user_agent: str) -> dict[str, str]:
        """Информация об UA"""
        try:
            ua = self._parse_user_agent(user_agent)
            return {
                "device_name": self._get_device_name(ua),
                "browser": ua.browser.family or "Other Browser",
                "platform": ua.os.family or "Unknown",
            }
        except Exception as e:
            logger.warning(f"Ошибка парсинга UA: {e}")
            return {
                "device_name": "Desktop",
                "browser": "Other Browser",
                "platform": "Unknown",
            }

    def _get_device_name(self, ua: UserAgent) -> str:
        """Определить устройство"""
        if ua.is_mobile:
            return "Mobile"
        elif ua.is_tablet:
            return "Tablet"
        elif ua.is_pc:
            return "Desktop"
        elif ua.is_bot:
            return "Bot"
        return "Desktop"

    def generate_fingerprint(
        self, request: Request, device_info: dict[str, Any] | None = None
    ) -> str:
        """Генерация fingerprint из запроса"""
        ua_string = request.META.get(self.META_USER_AGENT, "")
        if device_info is None:
            device_info = self.analyze_user_agent(ua_string)

        fingerprint_data = {
            "user_agent": ua_string,
            "accept_language": request.META.get(self.META_ACCEPT_LANGUAGE, ""),
            "accept_encoding": request.META.get(self.META_ACCEPT_ENCODING, ""),
            "accept_charset": request.META.get(self.META_ACCEPT_CHARSET, ""),
            "platform": device_info.get("platform", "Unknown"),
        }

        fingerprint = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:32]

    def extract_session_data(self, token: Token, request: Request) -> dict[str, Any]:
        """Извлечь данные для сессии"""
        user_id = token.payload.get("user_id")
        jti = token.payload.get("jti")

        if not user_id or not jti:
            raise ValueError("Токен должен содержать user_id и jti")

        ua_string = request.META.get(self.META_USER_AGENT, "")
        ip = self.get_client_ip(request)
        device_info = self.analyze_user_agent(ua_string)
        fingerprint = self.generate_fingerprint(request, device_info)

        return {
            "jti": jti,
            "user_id": user_id,
            "ip": ip,
            "fingerprint": fingerprint,
            **device_info,
        }

    def validate_fingerprint(self, stored_fingerprint: str, request: Request) -> bool:
        """Проверить fingerprint"""
        if not stored_fingerprint:
            return True

        current_fingerprint = self.generate_fingerprint(request)
        return stored_fingerprint == current_fingerprint


class SessionStorage:
    """
    Хранилище JWT-сессий в Redis
    """

    # Константы для ключей Redis (сокращенные названия для экономии памяти)
    KEY_PREFIX_SESSION = "s:"  # session:{jti}
    KEY_PREFIX_USER_SESSIONS = "u:"  # user_sessions:{user_id}
    KEY_PREFIX_FINGERPRINT = "f:"  # fingerprint_sessions:{fingerprint}

    DEFAULT_UNKNOWN = "Неизвестно"
    REVOKED_SESSION_TTL: int = settings.JWT_SESSION_SETTINGS.get(
        "REVOKED_SESSION_TTL", 7 * 24 * 60 * 60
    )

    @staticmethod
    def _decode_bytes(data: bytes | str) -> str:
        """Декодирует байты в строку"""
        return data.decode("utf-8") if isinstance(data, bytes) else data

    def __init__(self, cache_name: str = "sessions"):
        """Инициализация хранилища сессий из settings.CACHES"""
        self.cache = caches[cache_name]
        self.redis: Redis = self.cache.client.get_client()  # type: ignore[attr-defined]

    def create_session(self, extracted_data: dict[str, Any], ttl: int) -> str | None:
        """
        Создание сессии в Redis.

        :param extracted_data: Словарь данных из RequestExtractor.extract_session_data(token, request)
        :param ttl: Время жизни сессии в секундах
        :return: JTI созданной сессии
        """
        current_time = timezone.now()
        jti = extracted_data.get("jti")
        user_id = extracted_data.get("user_id")
        fingerprint = extracted_data.get("fingerprint")

        # Проверка обязательных полей
        if not all([jti, user_id, fingerprint]):
            logger.error(f"Недостаточно данных для создания сессии: {extracted_data}")
            raise ValueError("Для создания сессии необходимы jti, user_id и fingerprint")

        # Подготовка данных сессии
        session_data = {
            **extracted_data,
            "expires_at": (current_time + timedelta(seconds=ttl)).isoformat(),
            "created_at": current_time.isoformat(),
            "last_activity": current_time.isoformat(),
            "active": True,
        }

        # Пайплайн
        pipe: Pipeline = self.redis.pipeline()

        # 1. Устанавливаем данные
        session_key = f"{self.KEY_PREFIX_SESSION}{jti}"
        pipe.set(session_key, json.dumps(session_data, ensure_ascii=False), ex=ttl)

        # 2. Индекс по пользователю
        user_sessions_key = f"{self.KEY_PREFIX_USER_SESSIONS}{user_id}"
        pipe.sadd(user_sessions_key, jti)  # type: ignore[arg-type]
        pipe.expire(user_sessions_key, ttl)

        # 3. Индекс по fingerprint
        fingerprint_key = f"{self.KEY_PREFIX_FINGERPRINT}{fingerprint}"
        pipe.sadd(fingerprint_key, jti)  # type: ignore[arg-type]
        pipe.expire(fingerprint_key, ttl)

        # За один запрос к Redis
        pipe.execute()

        return jti  # ignore[assignment]

    def get_session(self, jti: str) -> dict[str, Any] | None:
        """
        Получение сессии по JTI из Redis
        Использует пайплайн для одновременного получения данных и TTL.
        Если TTL <= 0, возвращает None.

        :param jti: Идентификатор токена
        :return: Данные сессии или None если сессия не найдена или истекла
        """
        session_key = f"{self.KEY_PREFIX_SESSION}{jti}"
        pipe: Pipeline = self.redis.pipeline()
        pipe.get(session_key)
        pipe.ttl(session_key)

        data, ttl = pipe.execute()

        if not data or ttl <= 0:
            return None

        try:
            data = self._decode_bytes(data)
            return json.loads(data)  # type: ignore[no-any-return]
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON для сессии {jti}: {e}")
            return None

    def get_user_sessions(
        self,
        user_id: int,
        current_jti: str | None = None,
        active_only: bool = True,
        raw: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Получить сессии пользователя с опциональной фильтрацией по активности

        :param user_id: Идентификатор пользователя
        :param current_jti: JTI текущей сессии для флага is_current
        :param active_only: Если True, возвращает только активные сессии
        :param raw: Если True, возвращает "сырые" данные (для внутренней проверки)
        :return: Список отформатированных данных сессий, отсортированный по last_activity (новые сверху)
        """
        user_sessions_key = f"{self.KEY_PREFIX_USER_SESSIONS}{user_id}"
        jtis = self._get_set_members(user_sessions_key)

        if not jtis:
            return []

        sessions: list[dict[str, Any]] = []

        # Получаем все сессии
        pipe: Pipeline = self.redis.pipeline()

        for jti in jtis:
            pipe.get(f"{self.KEY_PREFIX_SESSION}{jti}")

        session_data_list = pipe.execute()

        # Выбираем функцию форматирования заранее
        def format_func(s):
            return s if raw else self._format_for_user(s, current_jti)

        # Заполнение данными списка сессий
        for jti, data in zip(jtis, session_data_list, strict=True):
            if not data:
                continue

            try:
                data = self._decode_bytes(data)
                session = json.loads(data)

                # Фильтрация по активности
                if active_only and not session.get("active", False):
                    continue

                # Используем заранее выбранную функцию
                sessions.append(format_func(session))

            except json.JSONDecodeError:
                logger.warning(f"Невалидный JSON для сессии {jti}, пропускаем")
                continue

        # Возвращаем список отсортированный список сессий
        sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        return sessions

    def update_session(self, jti: str, updates: dict[str, Any]) -> bool:
        """
        Обновление данных сессии

        :param jti: Идентификатор токена
        :param updates: Словарь параметров для обновления
        :return: True если обновление успешно, False если сессия не найдена либо истекла
        """
        session_key = f"{self.KEY_PREFIX_SESSION}{jti}"

        # Используем WATCH для безопасного обновления в конкурентной среде
        with self.redis.pipeline() as pipe:
            try:
                # Начинаем наблюдать за ключом, при определенных событиях перестаем наблюдать
                pipe.watch(session_key)

                data = pipe.get(session_key)
                if not data:
                    pipe.unwatch()
                    return False  # Сессия не существует

                data = self._decode_bytes(data)  # type: ignore[arg-type]
                session = json.loads(data)  # type: ignore[arg-type]
                session.update(updates)

                ttl = pipe.ttl(session_key)
                if ttl <= 0:  # type: ignore[operator]
                    pipe.unwatch()
                    return False  # Сессия истекла

                # Начинаем транзакцию
                pipe.multi()
                pipe.set(
                    session_key,
                    json.dumps(session, ensure_ascii=False, default=str),
                    ex=ttl,  # type: ignore[arg-type]
                )
                pipe.execute()

                return True

            except Exception as e:
                logger.error(f"Ошибка при обновлении сессии {jti}: {e}")
                return False

    def update_session_activity(self, jti: str) -> bool:
        """Обновить время последней активности сессии"""
        updates = {"last_activity": timezone.now().isoformat()}
        return self.update_session(jti, updates)

    def revoke_session(
        self, jti: str, user_id: str | None = None, reason: str = RevokeReasons.LOGOUT
    ) -> bool:
        """
        Отозвать сессию по JTI с очисткой индексов, отозванные храним 7 дней

        :param jti: Идентификатор токена
        :param user_id: ID пользователя (для проверки принадлежности)
        :param reason: Причина отзыва сессии
        :return: True если отзыв успешен
        """
        # Получаем данные сессии
        session = self.get_session(jti)
        if not session:
            return False

        if user_id is not None and session.get("user_id") != user_id:
            return False

        # Обновляем данные сессии
        updates = {
            "active": False,
            "revoked_at": timezone.now().isoformat(),
            "revoke_reason": reason,
        }

        pipe: Pipeline = self.redis.pipeline()
        self._prepare_revoke_operations(pipe, jti, session, updates)
        pipe.execute()

        return True

    def revoke_sessions_by_fingerprint(
        self, fingerprint: str, user_id: int | None = None, exclude_jti: str | None = None
    ) -> int:
        """
        Отозвать сессии по fingerprint

        Используется для безопасности: если обнаружена подозрительная активность.

        :param fingerprint: Отпечаток устройства
        :param user_id: Ограничить отзыв сессиями только этого пользователя (вдруг, если fp совпадет)
        :param exclude_jti: Исключить сессию с этим JTI из отзыва (например, текущую сессию)
        :return: Количество отозванных сессий
        """
        fingerprint_key = f"{self.KEY_PREFIX_FINGERPRINT}{fingerprint}"
        jtis = self._get_set_members(fingerprint_key)

        if not jtis:
            return 0

        # Один пайплайн для получения всех сессий
        pipe: Pipeline = self.redis.pipeline()
        jtis_to_fetch = [jti for jti in jtis if not (exclude_jti and jti == exclude_jti)]
        for jti in jtis_to_fetch:
            pipe.get(f"{self.KEY_PREFIX_SESSION}{jti}")

        session_data_list = pipe.execute()

        # Собираем сессии для отзыва
        sessions_to_revoke: list[tuple[str, dict[str, Any]]] = []

        for jti, data in zip(jtis_to_fetch, session_data_list, strict=True):
            if not data:
                continue

            try:
                data = self._decode_bytes(data)
                session = json.loads(data)

                if user_id and str(session.get("user_id")) != str(user_id):
                    continue

                sessions_to_revoke.append((jti, session))

            except json.JSONDecodeError:
                continue

        # Отзываем список сессий одним запросом к редис и получаем количество отозванных сессий
        revoked_count = self._revoke_sessions_batch(
            sessions_to_revoke, RevokeReasons.FINGERPRINT_CHANGED
        )
        return revoked_count

    def revoke_all_user_sessions(
        self, user_id: int, exclude_jti: str | None = None, reason: str = RevokeReasons.REVOKE_ALL
    ) -> int:
        """
        Отозвать все сессии пользователя с опцией оставить одну сессию

        Используется при смене пароля, выходе со всех устройств,
        или при обнаружении компрометации аккаунта.

        :param user_id: Идентификатор пользователя
        :param exclude_jti: Исключить сессию из отзыва
        :param reason: Причина отзыва сессий
        :return: Количество отозванных сессий
        """
        user_sessions_key = f"{self.KEY_PREFIX_USER_SESSIONS}{user_id}"
        jtis = self._get_set_members(user_sessions_key)

        if not jtis:
            return 0

        # Пайплайн для получения всех сессий
        pipe: Pipeline = self.redis.pipeline()
        jtis_to_fetch = [jti for jti in jtis if not (exclude_jti and jti == exclude_jti)]
        for jti in jtis_to_fetch:
            pipe.get(f"{self.KEY_PREFIX_SESSION}{jti}")

        session_data_list = pipe.execute()

        # Собираем сессии для отзыва
        sessions_to_revoke: list[tuple[str, dict[str, Any]]] = []

        for jti, data in zip(jtis_to_fetch, session_data_list, strict=True):
            if not data:
                continue

            try:
                data = self._decode_bytes(data)
                session = json.loads(data)
                sessions_to_revoke.append((jti, session))

            except json.JSONDecodeError:
                continue

        # Отзываем список сессий одним запросом к редис и получаем количество отозванных сессий
        revoked_count = self._revoke_sessions_batch(sessions_to_revoke, reason)
        return revoked_count

    def _prepare_revoke_operations(
        self, pipe: Pipeline, jti: str, session: dict[str, Any], updates: dict[str, Any]
    ) -> None:
        """Обновить сессию и удалить из индексов через пайплайн"""

        # 1. Изменяем данные сессии и храним сессию определенное количество времени
        session.update(updates)
        session_key = f"{self.KEY_PREFIX_SESSION}{jti}"
        pipe.set(
            session_key,
            json.dumps(session, ensure_ascii=False, default=str),
            ex=self.REVOKED_SESSION_TTL,
        )

        # 2. Удаляем из индекса пользователя
        user_id = session.get("user_id")
        if user_id:
            pipe.srem(f"{self.KEY_PREFIX_USER_SESSIONS}{user_id}", jti)

        # 3. Удаляем из индекса fingerprint
        fingerprint = session.get("fingerprint")
        if fingerprint:
            pipe.srem(f"{self.KEY_PREFIX_FINGERPRINT}{fingerprint}", jti)

    def _revoke_sessions_batch(
        self, sessions: list[tuple[str, dict[str, Any]]], reason: str
    ) -> int:
        """Метод для пакетного отзыва сессий"""

        if not sessions:
            return 0

        pipe: Pipeline = self.redis.pipeline()
        now = timezone.now().isoformat()

        for jti, session in sessions:
            updates = {
                "active": False,
                "revoked_at": now,
                "revoke_reason": reason,
            }
            self._prepare_revoke_operations(pipe, jti, session, updates)

        pipe.execute()

        return len(sessions)

    def _get_set_members(self, key: str) -> list[str]:
        """Получить элементы Redis множества (set) по ключу"""
        members = self.redis.smembers(key)
        if not members:
            return []
        return [self._decode_bytes(item) for item in members]  # type: ignore[union-attr]

    def get_all_sessions_sorted(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_suspicious: bool | None = None,
        device__in: str | None = None,
        browser__in: str | None = None,
        platform__in: str | None = None,
        suspicious_first: bool = True,
    ) -> dict[str, Any]:
        """
        Получить все активные сессии с сортировкой, пагинацией, поиском и фильтрами

        :param page: Номер страницы (1-based)
        :param page_size: Количество элементов на странице
        :param search: Поисковый запрос (email, ip, jti, fingerprint)
        :param is_suspicious: Фильтр по подозрительности (True/False/None)
        :param device__in: Фильтр по списку устройств (через запятую)
        :param browser__in: Фильтр по списку браузеров (через запятую)
        :param platform__in: Фильтр по списку ОС (через запятую)
        :param suspicious_first: Если True, подозрительные сверху; если False — обычные сверху
        :return: Dict с результатами и мета-данными пагинации
        """

        user_sessions_keys = self.redis.keys(f"{self.KEY_PREFIX_USER_SESSIONS}*")  # type: ignore[arg-type]

        if not user_sessions_keys:
            return {"results": [], "total": 0, "page": page, "page_size": page_size}

        # Собираем все JTI
        all_jtis: list[str] = []
        for key in user_sessions_keys:  # type: ignore[union-attr]
            members = self.redis.smembers(key)  # type: ignore[union-attr]
            if members:
                all_jtis.extend(self._decode_bytes(jti) for jti in members)  # type: ignore[union-attr]

        if not all_jtis:
            return {"results": [], "total": 0, "page": page, "page_size": page_size}

        # Один пайплайн для всех сессий
        pipe: Pipeline = self.redis.pipeline()
        for jti in all_jtis:
            pipe.get(f"{self.KEY_PREFIX_SESSION}{jti}")

        session_data_list = pipe.execute()

        # Обрабатываем и собираем user_id для получения email
        sessions = []
        user_ids = set()
        search_lower = search.lower() if search else None

        # Парсим списки для фильтров
        device_list = [d.strip() for d in device__in.split(",")] if device__in else None
        browser_list = [b.strip() for b in browser__in.split(",")] if browser__in else None
        platform_list = [p.strip() for p in platform__in.split(",")] if platform__in else None

        for jti, data in zip(all_jtis, session_data_list, strict=True):
            if not data:
                continue

            try:
                data = self._decode_bytes(data)
                session = json.loads(data)

                if not session.get("active", False):
                    continue

                formatted = self._format_for_admin(session)
                user_id = session.get("user_id")
                if user_id.isdigit():
                    user_ids.add(int(user_id))

                # Фильтр is_suspicious
                if is_suspicious is not None and formatted.get("is_suspicious") != is_suspicious:
                    continue

                # Фильтр по списку значений
                if device_list and formatted.get("device") not in device_list:
                    continue

                if browser_list and formatted.get("browser") not in browser_list:
                    continue

                if platform_list and formatted.get("platform") not in platform_list:
                    continue

                sessions.append((session["user_id"], formatted))

            except json.JSONDecodeError:
                logger.warning(f"Невалидный JSON для сессии {jti}, пропускаем")
                continue

        users_data = {
            str(user.user_id): user.email
            for user in UserAccount.objects.filter(user_id__in=user_ids).only("user_id", "email")
        }

        # Добавляем email и фильтруем по поиску
        filtered_sessions = []
        for user_id, session in sessions:
            session["user_email"] = users_data.get(str(user_id), "Unknown")

            # Поиск по email, ip, jti, fingerprint
            if search_lower:
                search_fields = [
                    session.get("user_email", "").lower(),
                    session.get("ip", "").lower(),
                    session.get("jti", "").lower(),
                    session.get("fingerprint", "").lower(),
                ]
                if not any(search_lower in field for field in search_fields):
                    continue

            filtered_sessions.append(session)

        # Сортировка: по is_suspicious + last_activity
        filtered_sessions.sort(
            key=lambda x: (
                x.get("is_suspicious", False),
                x.get("last_activity", ""),
            ),
            reverse=suspicious_first,
        )

        # Пагинация
        total = len(filtered_sessions)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = filtered_sessions[start:end]

        return {
            "results": paginated,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def _format_for_display(self, session: dict[str, Any]) -> dict[str, Any]:
        """Форматировать данные сессии для отображения в UI (для админа)"""

        def to_local_time(iso_string: str | None) -> str | None:
            """Конвертировать UTC строку в локальное время (TIME_ZONE)"""
            if not iso_string:
                return None
            return timezone.localtime(datetime.fromisoformat(iso_string)).isoformat()

        return {
            # === Идентификация ===
            "jti": session.get("jti", ""),
            "user_id": session.get("user_id"),
            # === Устройство ===
            "device": session.get("device_name", self.DEFAULT_UNKNOWN),
            "browser": session.get("browser", self.DEFAULT_UNKNOWN),
            "platform": session.get("platform", self.DEFAULT_UNKNOWN),
            # === Сеть ===
            "ip": session.get("ip", self.DEFAULT_UNKNOWN),
            "ip_changed": session.get("ip_changed", False),
            "new_ip": session.get("new_ip"),
            # === Безопасность ===
            "fingerprint": session.get("fingerprint", self.DEFAULT_UNKNOWN),
            "fingerprint_mismatch": session.get("fingerprint_mismatch", False),
            "last_mismatch": session.get("last_mismatch"),
            # === Время ===
            "created_at": to_local_time(session.get("created_at")),
            "last_activity": to_local_time(session.get("last_activity")),
            # === Статус ===
            "active": session.get("active", False),
            "revoked_at": to_local_time(session.get("revoked_at")),
            "revoke_reason": session.get("revoke_reason"),
        }

    def _format_for_user(
        self, session: dict[str, Any], current_jti: str | None = None
    ) -> dict[str, Any]:
        """Форматировать сессию для обычного пользователя"""
        formatted = self._format_for_display(session)
        return {
            "jti": formatted["jti"],
            "device": formatted["device"],
            "browser": formatted["browser"],
            "platform": formatted["platform"],
            "ip": formatted["ip"],
            "is_current": formatted["jti"] == current_jti if current_jti else False,
            "active": formatted["active"],
            "created_at": formatted["created_at"],
            "last_activity": formatted["last_activity"],
        }

    def _format_for_admin(self, session: dict[str, Any]) -> dict[str, Any]:
        """Форматировать сессию для админа (полные данные + флаги безопасности)"""
        formatted = self._format_for_display(session)
        formatted.pop("active", None)
        formatted.pop("revoked_at", None)
        formatted.pop("revoke_reason", None)
        formatted["is_suspicious"] = bool(
            formatted.get("fingerprint_mismatch") or formatted.get("ip_changed")
        )
        return formatted

    def get_session_stats(self) -> dict[str, int]:
        """Получить статистику по сессиям в Redis"""
        # Количество сессий
        total_sessions = len(self.redis.keys(f"{self.KEY_PREFIX_SESSION}*"))  # type: ignore[arg-type]

        # Количество пользователей с сессиями
        users_with_sessions = len(self.redis.keys(f"{self.KEY_PREFIX_USER_SESSIONS}*"))  # type: ignore[arg-type]

        return {
            "total_sessions": total_sessions,
            "users_with_sessions": users_with_sessions,
        }

    def cleanup_index(self, pattern: str) -> int:
        """Удаляет мёртвые JTI из индекса по паттерну"""
        removed = 0
        for key in self.redis.scan_iter(pattern, count=100):
            jtis = self.redis.smembers(key)  # type: ignore[union-attr, assignment]
            if not jtis:
                continue

            # Проверяем, какие сессии существуют
            pipe = self.redis.pipeline()
            for jti in jtis:  # type: ignore[union-attr]
                pipe.exists(f"{self.KEY_PREFIX_SESSION}{self._decode_bytes(jti)}")
            exists_list = pipe.execute()

            # Удаляем те, у которых нет сессии
            pipe = self.redis.pipeline()
            for jti, exists in zip(jtis, exists_list, strict=True):  # type: ignore[arg-type]
                if not exists:
                    pipe.srem(key, self._decode_bytes(jti))
                    removed += 1
            pipe.execute()

        return removed
