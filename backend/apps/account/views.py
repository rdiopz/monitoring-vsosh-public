import logging
from typing import Any

from django.conf import settings
from django.db import models, transaction
from django.db.models import F
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    generics,
    mixins,
    permissions,
    serializers,
    status,
    views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from apps.common.utils import audit_log

from .authentication import JWTManager
from .cache_service import SystemSettingCacheService
from .constants import Errors, Messages, RevokeReasons
from .filters import ApplicationFilter, AuditLogFilter, UserFilter
from .jwt_sessions import RequestExtractor
from .models import Application, AuditLog, SystemSetting, UserAccount, UserRole
from .permissions import IsAdministrator
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationReviewSerializer,
    ApplicationSerializer,
    ApplicationStatusSerializer,
    AuditLogSerializer,
    CodeVerifySerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    ProfileUpdateSerializer,
    RevokeAllUserSessionsSerializer,
    RevokeByFingerprintSerializer,
    SettingSerializer,
    UserRoleSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

logger = logging.getLogger(__name__)


class AuthenticatedRequest(Request):
    user: UserAccount  # type: ignore[assignment]


# =============================================================================
# Вспомогательные функции
# =============================================================================


def _model_to_dict_with_fk_ids(
    instance: models.Model,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    """
    Конвертирует модель в dict, заменяя ForeignKey на их ID.
    Например, из role в role_id, из reviewed_by в reviewed_by_id.
    """
    exclude = exclude or set()
    data = model_to_dict(instance, exclude=exclude)

    for field in instance._meta.fields:
        if field.is_relation and field.many_to_one:
            field_name = field.name
            if field_name in data:
                field_id = f"{field_name}_id"
                if hasattr(instance, field_id):
                    data[field_id] = getattr(instance, field_id)
                    del data[field_name]

    return data


def _get_audit_old_data(request: Request) -> dict | None:
    """Получить сохранённые старые данные из request"""
    return getattr(request, "_audit_old_data", None)


def _get_filtered_audit_data(request: Request, exclude: set[str] | None = None) -> dict | None:
    """Получить старые данные, исключая указанные поля"""
    data = _get_audit_old_data(request)
    if not data:
        return None
    exclude = exclude or set()
    return {k: v for k, v in data.items() if k not in exclude}


def _set_refresh_cookie(response: Response, refresh_token: str, request: Request) -> Response:
    """Вспомогательная функция для установки refresh token и флага в cookie"""
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=max_age,
        path="/api/auth/",
    )
    response.set_cookie(
        key="has_refresh_token",
        value="true",
        httponly=False,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=max_age,
        path="/",
    )

    return response


def _delete_refresh_cookie(response: Response) -> Response:
    """Вспомогательная функция для удаления refresh token и флага из cookie"""
    response.delete_cookie(
        key="refresh_token",
        path="/api/auth/",
        samesite="Lax",
    )
    response.delete_cookie(
        key="has_refresh_token",
        path="/",
        samesite="Lax",
    )
    return response


def _get_application_old_values(request: Request) -> dict | None:
    """Получить старые значения заявки"""
    return _get_filtered_audit_data(
        request, exclude={"application_datetime", "updated_at", "updated_by_id", "password_hash"}
    )


def _get_application_review_old_values(request: Request) -> dict | None:
    """Получить старые значения статуса заявки при рассмотрении"""
    return _get_filtered_audit_data(
        request,
        exclude={
            "application_id",
            "application_datetime",
            "password_hash",
            "review_comment",
            "updated_at",
            "updated_by_id",
        },
    )


def _get_setting_old_values(request: Request) -> dict | None:
    """Получить старое значение настройки"""
    return _get_filtered_audit_data(
        request, exclude={"setting_id", "key", "description", "updated_at", "updated_by_id"}
    )


def _get_user_old_values(request: Request) -> dict | None:
    """Получить старые значения пользователя"""
    return _get_filtered_audit_data(
        request,
        exclude={"password_hash", "last_login", "created_at", "updated_at", "password_changed_at"},
    )


def _get_me_old_values(request: Request) -> dict | None:
    """Получить старые значения профиля текущего пользователя"""
    return _get_filtered_audit_data(
        request,
        exclude={
            "user_id",
            "role",
            "role_id",
            "last_login",
            "created_at",
            "updated_at",
            "password_changed_at",
            "is_active",
        },
    )


def _parse_int_param(value: str | None, default: int, name: str) -> int:
    """Безопасный парсинг query-параметра"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError({name: Errors.QUERY_INT_PARAM.format(value=value)}) from None


# =============================================================================
# Views
# =============================================================================


class RoleListView(generics.ListAPIView):
    """Список всех ролей"""

    serializer_class = UserRoleSerializer
    permission_classes = [IsAdministrator]
    pagination_class = None

    def get_queryset(self):
        return UserRole.objects.all()


class LoginView(generics.GenericAPIView):
    """Вход в систему"""

    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @audit_log(action="вход", model="Пользователь", get_user_id=lambda data: data.get("user_id"))
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        response = Response(
            {
                "message": Messages.LOGIN_SUCCESS,
                "access": tokens.get("access"),
                "user_id": tokens.get("user_id"),
                "email": tokens.get("email"),
                "role": tokens.get("role"),
            },
            status=status.HTTP_200_OK,
        )

        _set_refresh_cookie(response, tokens.get("refresh"), request)
        return response


class RefreshTokenView(views.APIView):
    """Обновление токенов"""

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            logger.warning("Попытка обновления токена без refresh token в cookie")
            return Response(
                {"detail": Errors.REFRESH_TOKEN_NOT_FOUND},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            jwt_manager = JWTManager()
            result = jwt_manager.refresh_access_token(refresh_token, request)
            return Response(
                {
                    "message": Messages.TOKEN_REFRESHED,
                    "access": result.get("access"),
                },
                status=status.HTTP_200_OK,
            )

        except (InvalidToken, AuthenticationFailed) as e:
            logger.warning(f"Ошибка обновления токена: {e}")
            detail = str(e)
            if "Войдите в систему заново" not in detail:
                if not detail.endswith("."):
                    detail += "."
                detail += " Войдите в систему заново."
            response = Response({"detail": detail}, status=status.HTTP_401_UNAUTHORIZED)
            _delete_refresh_cookie(response)
            return response


# =============================================================================
# Сессии
# =============================================================================


class SessionViewSet(viewsets.ViewSet):
    """Управление сессиями пользователя"""

    lookup_field = "jti"

    def get_permissions(self) -> list:
        permissions_map: dict[tuple[str, ...], list[type[permissions.BasePermission]]] = {
            ("list", "logout", "logout_others", "destroy"): [permissions.IsAuthenticated],
            (
                "admin_list",
                "admin_destroy",
                "revoke_by_fingerprint",
                "revoke_all_user_sessions",
            ): [IsAdministrator],
        }

        for actions, permission_classes in permissions_map.items():
            if self.action in actions:
                return [permission() for permission in permission_classes]
        return [permissions.IsAuthenticated()]

    def list(self, request: AuthenticatedRequest) -> Response:
        """Список всех активных сессий пользователя (auth)"""
        jwt_manager = JWTManager()
        auth = request.auth
        current_jti = auth.payload.get("jti") if auth else None  # type: ignore[union-attr]

        sessions = jwt_manager.get_user_sessions(
            user_id=request.user.user_id,
            current_jti=current_jti or "",
        )

        return Response(
            {"count": len(sessions), "results": sessions},
            status=status.HTTP_200_OK,
        )

    @audit_log(action="выход", model="Сессия")
    @action(detail=False, methods=["post"])
    def logout(self, request: AuthenticatedRequest) -> Response:
        """Выход из текущей сессии (auth)"""
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            jwt_manager = JWTManager()
            jwt_manager.revoke_refresh_token(refresh_token)

        response = Response({"message": Messages.LOGOUT_SUCCESS}, status=status.HTTP_200_OK)
        _delete_refresh_cookie(response)
        return response

    @audit_log(
        action="завершение сессии",
        model="Сессия",
        get_old_values=lambda request: (
            {"jti": request.auth.payload.get("jti")}
            if request.auth and hasattr(request.auth, "payload")
            else {}
        ),
    )
    def destroy(self, request: AuthenticatedRequest, jti: str | None = None) -> Response:
        """Выход из конкретной сессии по JTI"""
        jwt_manager = JWTManager()
        auth = request.auth
        current_jti = auth.payload.get("jti") if auth else None  # type: ignore[union-attr]

        if jti == current_jti:
            return Response(
                {"detail": Errors.CANNOT_REVOKE_CURRENT_SESSION},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success = jwt_manager.revoke_session(jti=jti or "", user_id=str(request.user.user_id))

        if not success:
            return Response(
                {"detail": Errors.SESSION_REVOKED_OR_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"message": Messages.SESSION_TERMINATED}, status=status.HTTP_200_OK)

    @audit_log(action="выход из других сессий", model="Сессия")
    @action(detail=False, methods=["post"], url_path="logout-others")
    def logout_others(self, request: AuthenticatedRequest) -> Response:
        """Выход из всех сессий кроме текущей"""
        jwt_manager = JWTManager()
        auth = request.auth
        current_jti = auth.payload.get("jti") if auth else None  # type: ignore[union-attr]

        revoked_count = jwt_manager.revoke_other_user_sessions(
            user_id=request.user.user_id,
            exclude_jti=current_jti or "",
        )

        return Response(
            {
                "message": Messages.SESSIONS_REVOKED.format(count=revoked_count),
                "revoked_count": revoked_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="all")
    def admin_list(self, request: AuthenticatedRequest) -> Response:
        """Все сессии с параметрами (admin)"""
        jwt_manager = JWTManager()

        page = _parse_int_param(request.query_params.get("page"), default=1, name="page")
        page_size = _parse_int_param(
            request.query_params.get("page_size"), default=20, name="page_size"
        )

        search = request.query_params.get("search")
        is_suspicious_param = request.query_params.get("is_suspicious")
        device__in = request.query_params.get("device__in")
        browser__in = request.query_params.get("browser__in")
        platform__in = request.query_params.get("platform__in")

        is_suspicious = None
        if is_suspicious_param is not None:
            is_suspicious = is_suspicious_param.lower() == "true"

        suspicious_first_param = request.query_params.get("suspicious_first")
        suspicious_first = True
        if suspicious_first_param is not None:
            suspicious_first = suspicious_first_param.lower() == "true"

        result = jwt_manager.get_all_sessions_sorted(
            page=page,
            page_size=page_size,
            search=search,
            is_suspicious=is_suspicious,
            device__in=device__in,
            browser__in=browser__in,
            platform__in=platform__in,
            suspicious_first=suspicious_first,
        )

        stats = jwt_manager.get_session_stats()

        return Response(
            {
                **result,
                "total_stats": stats,
            },
            status=status.HTTP_200_OK,
        )

    @audit_log(action="завершение сессии", model="Сессия")
    @action(detail=False, methods=["delete"], url_path="admin/(?P<jti>[^/.]+)")
    def admin_destroy(self, request: AuthenticatedRequest, jti: str) -> Response:
        """Завершить конкретную сессию по JTI (admin)"""
        jwt_manager = JWTManager()

        auth = request.auth
        current_jti = auth.payload.get("jti") if auth else None  # type: ignore[union-attr]

        if jti == current_jti:
            return Response(
                {"detail": Errors.CANNOT_REVOKE_CURRENT_SESSION},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success = jwt_manager.revoke_session(jti=jti, reason=RevokeReasons.REVOKE_OTHER)

        if not success:
            return Response(
                {"detail": Errors.SESSION_REVOKED_OR_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"message": Messages.SESSION_TERMINATED}, status=status.HTTP_200_OK)

    @audit_log(
        action="завершение сессий по отпечатку",
        model="Сессия",
    )
    @action(detail=False, methods=["post"], url_path="revoke-by-fingerprint")
    def revoke_by_fingerprint(self, request: AuthenticatedRequest) -> Response:
        """Завершить все сессии с указанным fingerprint (admin)"""
        serializer = RevokeByFingerprintSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth = request.auth
        current_jti = auth.payload.get("jti") if auth else None  # type: ignore[union-attr]

        fingerprint = serializer.validated_data["fingerprint"]
        user_id = serializer.validated_data.get("user_id") or None
        exclude_jti = serializer.validated_data.get("exclude_jti") or current_jti

        request_extractor = RequestExtractor()
        current_fingerprint = request_extractor.generate_fingerprint(request)

        if fingerprint == current_fingerprint:
            return Response(
                {"detail": Errors.CANNOT_REVOKE_SESSIONS_BY_FP},
                status=status.HTTP_400_BAD_REQUEST,
            )

        jwt_manager = JWTManager()
        revoked_count = jwt_manager.revoke_sessions_by_fingerprint(
            fingerprint=fingerprint,
            user_id=user_id,
            exclude_jti=exclude_jti,
        )

        return Response(
            {
                "message": Messages.SESSIONS_REVOKED.format(count=revoked_count),
                "revoked_count": revoked_count,
            },
            status=status.HTTP_200_OK,
        )

    @audit_log(
        action="завершение всех сессий пользователя",
        model="Сессия",
    )
    @action(detail=False, methods=["post"], url_path="revoke-all-user-sessions")
    def revoke_all_user_sessions(self, request: AuthenticatedRequest) -> Response:
        """Завершить все сессии указанного пользователя (admin)"""
        serializer = RevokeAllUserSessionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        exclude_jti = serializer.validated_data.get("exclude_jti")

        auth = request.auth
        current_jti = auth.payload.get("jti") if auth else None  # type: ignore[union-attr]

        if user_id == request.user.user_id and current_jti != exclude_jti:
            return Response(
                {"detail": Errors.CANNOT_ACT_ON_SELF},
                status=status.HTTP_400_BAD_REQUEST,
            )

        jwt_manager = JWTManager()
        revoked_count = jwt_manager.revoke_all_user_sessions(
            user_id=user_id,
            exclude_jti=exclude_jti or None,
        )

        return Response(
            {
                "message": Messages.SESSIONS_REVOKED.format(count=revoked_count),
                "revoked_count": revoked_count,
            },
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Заявки
# =============================================================================


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    Управление заявками на доступ к системе.

    list: Список всех заявок (admin).
    retrieve: Детали заявки по ID (admin).
    """

    queryset = Application.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ApplicationFilter
    search_fields = ["email", "review_comment", "reviewed_by__email"]
    ordering_fields = [
        "application_id",
        "email",
        "status",
        "application_datetime",
        "updated_at",
        "reviewed_by_email",
    ]
    ordering = ["-application_datetime"]

    _serializers = {
        "review": ApplicationReviewSerializer,
        "check_status": ApplicationStatusSerializer,
        "create": ApplicationCreateSerializer,
    }

    _permissions: dict[tuple[str, ...], list[type[permissions.BasePermission]]] = {
        ("create", "check_status"): [permissions.AllowAny],
        ("list", "retrieve", "review", "destroy", "update", "partial_update"): [IsAdministrator],
    }

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от метода"""
        return self._serializers.get(self.action, ApplicationSerializer)

    def get_permissions(self) -> list:
        """Возвращает список разрешений в зависимости от метода"""
        for actions, permission_classes in self._permissions.items():
            if self.action in actions:
                return [permission() for permission in permission_classes]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Возвращает queryset с оптимизацией для review"""
        queryset = super().get_queryset()
        if self.action == "review":
            return queryset.only(
                "application_id",
                "email",
                "password_hash",
                "status",
                "application_datetime",
                "review_comment",
                "updated_at",
                "reviewed_by",
            )
        elif self.action in ["list", "retrieve"]:
            return queryset.annotate(reviewed_by_email=models.F("reviewed_by__email")).values(
                "application_id",
                "email",
                "status",
                "application_datetime",
                "review_comment",
                "updated_at",
                "reviewed_by_email",
            )
        return queryset

    def perform_create(self, serializer):
        """Переопределение: сохраняем instance для логов"""
        super().perform_create(serializer)
        self.request._audit_instance = serializer.instance

    def perform_update(self, serializer):
        """Переопределение: сохраняем старые данные для логов"""
        self.request._audit_old_data = _model_to_dict_with_fk_ids(serializer.instance)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """Переопределение: сохраняем старые данные для логов"""
        self.request._audit_old_data = _model_to_dict_with_fk_ids(instance)
        super().perform_destroy(instance)

    @audit_log(
        action="создание",
        model="Заявка",
        model_class=Application,
    )
    def create(self, request: Request, *args, **kwargs):
        """Создать заявку (public)"""
        return super().create(request, *args, **kwargs)

    @audit_log(
        action="обновление",
        model="Заявка",
        model_class=Application,
        get_old_values=_get_application_old_values,
    )
    def update(self, request: Request, *args, **kwargs):
        """Полностью обновить заявку (admin)"""
        return super().update(request, *args, **kwargs)

    @audit_log(
        action="обновление",
        model="Заявка",
        model_class=Application,
        get_old_values=_get_application_old_values,
    )
    def partial_update(self, request: Request, *args, **kwargs):
        """Частично обновить заявку (admin)"""
        return super().partial_update(request, *args, **kwargs)

    @audit_log(
        action="удаление",
        model="Заявка",
        model_class=Application,
        get_old_values=_get_application_old_values,
    )
    def destroy(self, request: Request, *args, **kwargs):
        """Удалить заявку (admin)"""
        return super().destroy(request, *args, **kwargs)

    @audit_log(
        action="рассмотрение",
        model="Заявка",
        model_class=Application,
        get_old_values=_get_application_review_old_values,
        get_new_values=lambda request, data: (
            {"user_id": data.get("user_id")} if data.get("user_id") else None
        ),
    )
    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request: Request, pk: int | None = None) -> Response:
        """Рассмотреть заявку и если одобрена, то назначить пользователя (admin)"""
        instance = self.get_object()
        self.request._audit_old_data = _model_to_dict_with_fk_ids(instance)  # type: ignore[attr-defined]
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="check-status")
    def check_status(self, request: Request) -> Response:
        """Проверить статус по email (public)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.get_status()  # type: ignore[attr-defined]
        return Response(data, status=status.HTTP_200_OK)


# =============================================================================
# Пользователи
# =============================================================================


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Управление пользователями.

    list: Список всех пользователей (admin).
    retrieve: Детали пользователя по ID (admin).
    """

    queryset = UserAccount.objects.select_related("role").annotate(role_name=F("role__name"))
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["email", "role__name"]
    ordering_fields = [
        "user_id",
        "email",
        "last_login",
        "created_at",
        "updated_at",
        "password_change_at",
        "role_name",
    ]
    ordering = ["email"]

    _serializers = {
        "me": ProfileUpdateSerializer,
        "update": UserUpdateSerializer,
        "partial_update": UserUpdateSerializer,
        "me_change_password": PasswordChangeSerializer,
    }

    _permissions: dict[tuple[str, ...], list[type[permissions.BasePermission]]] = {
        ("list", "retrieve", "update", "partial_update", "reviewers"): [IsAdministrator],
        ("me", "me_change_password"): [permissions.IsAuthenticated],
    }

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от метода"""
        if self.action == "me" and self.request.method in permissions.SAFE_METHODS:
            return UserSerializer

        return self._serializers.get(self.action, UserSerializer)

    def get_permissions(self) -> list:
        """Возвращает список разрешений в зависимости от метода"""
        for actions, permission_classes in self._permissions.items():
            if self.action in actions:
                return [permission() for permission in permission_classes]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        """Переопределение: сохраняем старые данные для логов"""
        self.request._audit_old_data = _model_to_dict_with_fk_ids(serializer.instance)
        super().perform_update(serializer)

    @audit_log(
        action="обновление",
        model="Пользователь",
        model_class=UserAccount,
        get_old_values=_get_me_old_values,
    )
    @action(detail=False, methods=["get", "put", "patch"], url_path="me")
    def me(self, request: AuthenticatedRequest) -> Response:
        """Профиль текущего пользователя (auth)"""
        if request.method in ("PUT", "PATCH"):
            self.request._audit_old_data = _model_to_dict_with_fk_ids(request.user)  # type: ignore[attr-defined]
            serializer = self.get_serializer(
                request.user, data=request.data, partial=request.method == "PATCH"
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.get_serializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @audit_log(
        action="смена пароля",
        model="Пользователь",
        model_class=UserAccount,
    )
    @action(detail=False, methods=["post"], url_path="me/change-password")
    def me_change_password(self, request: AuthenticatedRequest) -> Response:
        """Смена пароля для текущего пользователя (auth)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": Messages.PASSWORD_CHANGED}, status=status.HTTP_200_OK)

    @audit_log(
        action="обновление",
        model="Пользователь",
        model_class=UserAccount,
        get_old_values=_get_user_old_values,
    )
    def update(self, request: Request, *args, **kwargs):
        """Полностью обновить пользователя (admin)"""
        return super().update(request, *args, **kwargs)

    @audit_log(
        action="обновление",
        model="Пользователь",
        model_class=UserAccount,
        get_old_values=_get_user_old_values,
    )
    def partial_update(self, request: Request, *args, **kwargs):
        """Частично обновить пользователя (admin)"""
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="reviewers")
    def reviewers(self, request: AuthenticatedRequest) -> Response:
        """Получить список админов, которые рассматривали заявки (admin)"""
        reviewers = (
            UserAccount.objects.filter(reviewed_applications__isnull=False)
            .distinct()
            .values("user_id", "email")
            .order_by("email")
        )
        return Response(reviewers, status=status.HTTP_200_OK)


# =============================================================================
# Настройки
# =============================================================================


class SettingViewSet(viewsets.GenericViewSet):
    """Управление настройками системы"""

    lookup_field = "key"
    queryset = SystemSetting.objects.all()

    _serializers: dict[str, type[serializers.Serializer]] = {
        "update": SettingSerializer,
        "verify_code": CodeVerifySerializer,
    }

    _permissions: dict[tuple[str, ...], list[type[permissions.BasePermission]]] = {
        ("list", "update"): [IsAdministrator],
        ("monitoring_years",): [permissions.IsAuthenticated],
        ("verify_code",): [permissions.AllowAny],
    }

    def get_serializer_class(self) -> type[serializers.Serializer]:
        """Возвращает класс сериализатора в зависимости от действия"""
        return self._serializers.get(self.action, serializers.Serializer)

    def get_serializer(self, *args, **kwargs) -> serializers.Serializer:
        """Создаёт экземпляр сериализатора с параметрами"""
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()

        if self.action == "update":
            kwargs["context"]["setting_key"] = self.kwargs.get("key")

        return serializer_class(*args, **kwargs)

    def get_permissions(self) -> list:
        """Возвращает список разрешений в зависимости от действия"""
        for actions, permission_classes in self._permissions.items():
            if self.action in actions:
                return [permission() for permission in permission_classes]
        return [permissions.IsAuthenticated()]

    def list(self, request: Request) -> Response:
        """Список всех настроек (admin)"""
        settings_list = SystemSetting.objects.select_related("updated_by").values(
            "key", "value", "description", "updated_at", "updated_by__email"
        )
        return Response(settings_list, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="monitoring-years")
    def monitoring_years(self, request: Request) -> Response:
        """Получить период мониторинга (auth)"""
        cached = SystemSettingCacheService.get_monitoring_years()
        if cached:
            return Response({"monitoring_years": cached}, status=status.HTTP_200_OK)

        setting = get_object_or_404(SystemSetting, key="monitoring_years")
        SystemSettingCacheService.set_monitoring_years(setting.value)
        return Response({"monitoring_years": setting.value}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="verify-code")
    def verify_code(self, request: Request) -> Response:
        """Проверить код доступа (public)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": Messages.CODE_VALID}, status=status.HTTP_200_OK)

    @audit_log(
        action="обновление",
        model="Настройка",
        model_class=SystemSetting,
        get_old_values=_get_setting_old_values,
    )
    @transaction.atomic
    def update(self, request: AuthenticatedRequest, key: str) -> Response:
        """Обновить настройку по ключу (admin)"""
        setting = get_object_or_404(SystemSetting.objects.select_for_update(), key=key)
        self.request._audit_old_data = _model_to_dict_with_fk_ids(setting)  # type: ignore[attr-defined]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        setting.value = serializer.validated_data["value"]
        setting.updated_by = request.user
        setting.save(update_fields=["value", "updated_by", "updated_at"])

        if setting.key == "monitoring_years":
            SystemSettingCacheService.invalidate_monitoring_years()

        return Response(
            {
                "message": Messages.SETTING_UPDATE,
                "setting_id": setting.setting_id,
                "key": key,
                "value": setting.value,
            },
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Аудит
# =============================================================================


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Просмотр логов аудита (admin).

    list: Список всех логов с фильтрами, поиском и сортировкой.
    retrieve: Детали лога по ID.
    """

    queryset = (
        AuditLog.objects.annotate(user_email=F("user__email"))
        .only(
            "log_id",
            "timestamp",
            "user_id",
            "action",
            "model_name",
            "object_id",
            "request_data",
            "old_values",
            "new_values",
            "ip_address",
        )
        .order_by("-timestamp")
    )
    permission_classes = [IsAdministrator]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    serializer_class = AuditLogSerializer
    filterset_class = AuditLogFilter
    ordering_fields = [
        "log_id",
        "timestamp",
        "user_email",
        "action",
        "model_name",
        "object_id",
        "ip_address",
    ]
    ordering = ["-timestamp"]
    search_fields = ["user__email", "ip_address"]

    @action(detail=False, methods=["get"], url_path="filters")
    def filters(self, request: Request) -> Response:
        """Получить уникальные значения для фильтров (actions, models)"""
        actions = list(
            AuditLog.objects.values_list("action", flat=True).distinct().order_by("action")
        )
        models = list(
            AuditLog.objects.values_list("model_name", flat=True).distinct().order_by("model_name")
        )

        return Response({"actions": actions, "models": models})
