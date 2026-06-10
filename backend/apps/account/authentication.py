import logging
from typing import Any

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, Token

from .cache_service import UserService
from .constants import Errors, RevokeReasons
from .jwt_sessions import SessionService
from .models import UserAccount

logger = logging.getLogger(__name__)


class CustomJWTAuthentication(JWTAuthentication):
    """Кастомный JWT аутентификация с Redis Sessions"""

    def __init__(self, *args, **kwargs):
        """Инициализирует JWTAuthentication с сервисом сессии для валидации"""
        super().__init__(*args, **kwargs)
        self.sessions = SessionService()

    def authenticate(self, request: Request) -> tuple[UserAccount, Token] | None:  # type: ignore[override]
        """Переопределенный метод authenticate для получения request"""
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token, request)

        return self.get_user(validated_token), validated_token

    def get_validated_token(self, raw_token: bytes, request: Request) -> Token:  # type: ignore[override]
        """Проверка токена"""
        # Все стандартные проверки
        try:
            token = super().get_validated_token(raw_token)
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Ошибка валидации токена: {e}")
            raise InvalidToken(Errors.TOKEN_INVALID) from e

        # Проверка сессии через session service
        jti = token.payload.get("jti")

        if jti:
            is_valid, message = self.sessions.validate_session(jti=jti, request=request)

            if not is_valid:
                logger.warning(f"Невалидная сессия: {message}")
                raise InvalidToken(message)

            # Обновляем активность сессии при успешной проверке
            self.sessions.storage.update_session_activity(jti)

        return token

    def get_user(self, validated_token: Token) -> UserAccount:  # type: ignore[override]
        """Получение пользователя по токену"""
        try:
            user_id = validated_token.payload.get("user_id")

            if not user_id:
                raise AuthenticationFailed(Errors.TOKEN_INVALID)

            # Кэширование через сервис
            user = UserService.get_cached_user(user_id)

            # Проверка заблокированности
            if not UserService.is_user_active(user):
                logger.warning(f"Попытка входа заблокированного пользователя: {user.email}")
                raise AuthenticationFailed(Errors.ACCOUNT_BLOCKED)

            logger.debug(f"Успешная аутентификация пользователя: {user.email}")
            return user

        except UserAccount.DoesNotExist:
            logger.warning(f"Попытка входа с несуществующим user_id: {user_id}")
            raise AuthenticationFailed(Errors.USER_NOT_FOUND) from None


class JWTManager:
    """Класс управление токенами"""

    def __init__(self):
        """Инициализирует менеджер JWT с сервисом сессий"""
        self.sessions = SessionService()

    def create_tokens_for_user(self, user: UserAccount, request: Request) -> dict[str, Any]:
        """Создание Access и Refresh токенов"""
        refresh = RefreshToken.for_user(user)  # type: ignore[type-var]
        refresh["email"] = user.email
        refresh["role"] = user.role.name if user.role else None

        access = refresh.access_token
        access["jti"] = refresh.payload.get("jti")
        access["email"] = user.email
        access["role"] = user.role.name if user.role else None

        self.sessions.add_session(refresh, request)

        return {
            "refresh": str(refresh),
            "access": str(access),
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.name if user.role else None,
        }

    def refresh_access_token(self, refresh_token: str, request: Request) -> dict[str, str]:
        """Обновление Access токена"""
        try:
            user, jti = self._validate_refresh_token(refresh_token, request)

            access = AccessToken.for_user(user)  # type: ignore[type-var]
            access["jti"] = jti
            access["email"] = user.email
            access["role"] = user.role.name if user.role else None

            if jti:
                self.sessions.storage.update_session_activity(jti)

            return {"access": str(access)}

        except TokenError as e:
            raise InvalidToken(str(e)) from e
        except UserAccount.DoesNotExist:
            raise AuthenticationFailed(Errors.USER_NOT_FOUND) from None

    def refresh_tokens(self, refresh_token: str, request: Request) -> dict[str, Any]:
        """Обновление обоих токенов"""
        try:
            user, jti = self._validate_refresh_token(refresh_token, request)

            # Отзываем старую сессию
            if jti:
                self.sessions.storage.revoke_session(jti=jti, reason=RevokeReasons.UPDATE)

            # Создаем новые токены
            return self.create_tokens_for_user(user, request)

        except TokenError as e:
            raise InvalidToken(str(e)) from e
        except UserAccount.DoesNotExist:
            raise AuthenticationFailed(Errors.USER_NOT_FOUND) from None

    def get_user_sessions(
        self, user_id: int, current_jti: str, active_only: bool = True
    ) -> list[dict[str, Any]]:
        """Получить активные сессии пользователя"""
        return self.sessions.storage.get_user_sessions(
            user_id, current_jti=current_jti, active_only=active_only
        )

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
        """Получить все сессии с пагинацией, поиском и фильтрами (для админа)"""
        return self.sessions.storage.get_all_sessions_sorted(
            page=page,
            page_size=page_size,
            search=search,
            is_suspicious=is_suspicious,
            device__in=device__in,
            browser__in=browser__in,
            platform__in=platform__in,
            suspicious_first=suspicious_first,
        )

    def get_session_stats(self) -> dict[str, int]:
        """Получить статистику по сессиям"""
        return self.sessions.storage.get_session_stats()

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Отозвать Refresh токен"""
        try:
            token = RefreshToken(refresh_token)  # type: ignore[arg-type]
            jti = token.payload.get("jti")
            if jti:
                return self.sessions.storage.revoke_session(jti=jti, reason=RevokeReasons.LOGOUT)
            return False
        except Exception as e:
            logger.error(f"Ошибка при отзыве токена: {e}")
            return False

    def revoke_session(
        self, jti: str, user_id: str | None = None, reason: str = RevokeReasons.REVOKE_OTHER
    ) -> bool:
        """Отозвать конкретную сессию по JTI"""
        return self.sessions.storage.revoke_session(jti=jti, user_id=user_id, reason=reason)

    def revoke_other_user_sessions(
        self, user_id: int, exclude_jti: str, reason: str = RevokeReasons.REVOKE_OTHERS
    ) -> int:
        """Отозвать все сессии пользователя, кроме своей"""
        return self.sessions.storage.revoke_all_user_sessions(
            user_id=user_id, exclude_jti=exclude_jti, reason=reason
        )

    def revoke_sessions_by_fingerprint(
        self,
        fingerprint: str,
        user_id: int | None = None,
        exclude_jti: str | None = None,
    ) -> int:
        """Отозвать сессии по fingerprint"""
        return self.sessions.storage.revoke_sessions_by_fingerprint(
            fingerprint=fingerprint, user_id=user_id, exclude_jti=exclude_jti
        )

    def revoke_all_user_sessions(
        self,
        user_id: int,
        exclude_jti: str | None = None,
        reason: str = RevokeReasons.REVOKE_ALL,
    ) -> int:
        """Отозвать все сессии пользователя"""
        return self.sessions.storage.revoke_all_user_sessions(
            user_id=user_id, exclude_jti=exclude_jti, reason=reason
        )

    def _validate_refresh_token(
        self, refresh_token: str, request: Request
    ) -> tuple[UserAccount, str | None]:
        """Валидация refresh токена и получение пользователя"""
        token = RefreshToken(refresh_token)  # type: ignore[arg-type]
        jti = token.payload.get("jti")
        user_id = token.payload.get("user_id")

        if not user_id:
            raise InvalidToken(Errors.TOKEN_INVALID)

        # Проверка сессии
        if jti:
            is_valid, message = self.sessions.validate_session(jti=jti, request=request)
            if not is_valid:
                raise InvalidToken(message)

        # Кэширование через сервис
        user = UserService.get_cached_user(user_id)

        # Проверка заблокированности
        if not UserService.is_user_active(user):
            raise AuthenticationFailed(Errors.ACCOUNT_BLOCKED)

        return user, jti
