import logging
import re
from typing import Any, cast

from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import exceptions, serializers
from rest_framework.request import Request
from rest_framework.serializers import ValidationError

from apps.common.serializers import FlexibleModelSerializer, get_field_error_messages

from .authentication import JWTManager
from .cache_service import UserService
from .constants import Errors, Messages, RevokeReasons
from .models import Application, AuditLog, SystemSetting, UserAccount, UserRole

logger = logging.getLogger(__name__)

# =============================================================================
# Вспомогательные функции
# =============================================================================


def validate_registration_code(value: str):
    """
    Кастомный валидатор для проверки кода регистрации.
    Используется в CodeVerifySerializer и ApplicationCreateSerializer.
    """
    code = value.strip()

    if len(code) < 6 or len(code) > 24:
        raise ValidationError(Errors.INVALID_CODE)

    valid_code = (
        SystemSetting.objects.filter(key="registration_code")
        .values_list("value", flat=True)
        .first()
    )

    if not valid_code or code != valid_code:
        raise ValidationError(Errors.INVALID_CODE)

    return code


# =============================================================================
# Роли
# =============================================================================


class UserRoleSerializer(serializers.ModelSerializer):
    """Роль"""

    class Meta:
        model = UserRole
        fields = ["role_id", "name"]


# =============================================================================
# Заявки
# =============================================================================


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания заявки на регистрацию.
    Используется на втором этапе после проверки кода.
    """

    password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "Заполните пароль",
            "blank": "Пароль не может быть пустым",
        },
    )

    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "Заполните подтверждение пароля",
            "blank": "Подтверждение пароля не может быть пустым",
        },
    )

    registration_code = serializers.CharField(
        write_only=True,
        validators=[validate_registration_code],
    )

    class Meta:
        model = Application
        fields = ("email", "password", "confirm_password", "registration_code")

    def validate_email(self, value: str) -> str:
        """Валидация и нормализация email адреса"""
        email = value.strip().lower()

        if UserAccount.objects.filter(email=email).exists():
            raise serializers.ValidationError(Errors.EMAIL_REGISTERED)

        return email

    def validate_password(self, value: str) -> str:
        """Валидация пароля по требованиям безопасности"""
        password = value.strip()
        email = self.initial_data.get("email", "")

        # Временный объект для валидации
        user_for_validation = UserAccount(email=email)
        password_validation.validate_password(password, user=user_for_validation)  # type: ignore[arg-type]

        return password

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Общая валидация данных: совпадение паролей"""
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({"password": Errors.PASSWORDS_MISMATCH})

        attrs.pop("confirm_password", None)
        attrs.pop("registration_code", None)

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Application:
        """Создание заявки на регистрацию с хэшированием пароля"""
        password = validated_data.pop("password")
        password_hash = make_password(password)

        instance = Application.objects.create(
            email=validated_data["email"],
            password_hash=password_hash,
            status="рассматривается",
        )

        return instance

    def to_representation(self, instance: Application) -> dict[str, Any]:
        """Отправка ответа в таком формате"""
        return {
            "message": Messages.APPLICATION_CREATED,
            "application_id": instance.application_id,
        }


class ApplicationSerializer(FlexibleModelSerializer):
    """Сериализатор заявок для CRUD операций"""

    reviewed_by_email = serializers.CharField(read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={
            "blank": "Пароль не может быть пустым",
        },
    )

    class Meta:
        model = Application
        fields = (
            "application_id",
            "email",
            "status",
            "application_datetime",
            "reviewed_by_email",
            "review_comment",
            "updated_at",
            "password",
        )
        read_only_fields = ("application_id", "application_datetime", "updated_at")
        extra_kwargs: dict[str, Any] = {
            "email": {
                "error_messages": get_field_error_messages(Application, "email"),
            },
            "status": {
                "error_messages": get_field_error_messages(Application, "status"),
            },
            "review_comment": {
                "error_messages": get_field_error_messages(Application, "review_comment"),
            },
        }

    def validate_password(self, value: str) -> str:
        """Валидация пароля по требованиям безопасности"""
        if not value:
            return value

        password = value.strip()
        email = self.initial_data.get("email", "")

        # Временный объект для валидации
        user_for_validation = UserAccount(email=email)
        password_validation.validate_password(password, user=user_for_validation)  # type: ignore[arg-type]

        return password

    def update(self, instance: Application, validated_data: dict[str, Any]) -> Application:
        """Обновление заявки с возможностью смены пароля"""
        password = validated_data.pop("password", None)

        if password:
            validated_data["password_hash"] = make_password(password)

        return super().update(instance, validated_data)


class ApplicationStatusSerializer(serializers.Serializer):
    """Для проверки статуса заявки"""

    email = serializers.EmailField(
        error_messages={
            "required": "Заполните email",
            "blank": "Email не может быть пустым",
            "invalid": "Введите корректный email",
        }
    )

    def get_status(self) -> dict[str, str]:
        """Запрос на получение статуса по email"""
        email = self.validated_data["email"].strip().lower()

        status = Application.objects.filter(email=email).values_list("status", flat=True).first()

        return {"status": str(status) if status else "отсутствует"}


class ApplicationReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для рассмотрения заявки администратором"""

    status = serializers.ChoiceField(
        choices=["предоставлен", "отклонён"],
        write_only=True,
        error_messages={
            "required": "Выберите решение по заявке",
            "invalid_choice": "Статус должен быть 'предоставлен' или 'отклонён'",
        },
    )

    role_id = serializers.IntegerField(
        write_only=True,
        required=False,
        error_messages={
            "invalid": "Введите корректный ID роли",
        },
    )

    class Meta:
        model = Application
        fields = ["status", "review_comment", "role_id"]
        read_only_fields = ["reviewed_by"]
        extra_kwargs: dict[str, Any] = {
            "review_comment": {
                "error_messages": get_field_error_messages(Application, "review_comment"),
            },
        }

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Общая валидация"""
        status = attrs.get("status")
        role_id = attrs.get("role_id")

        if status == "предоставлен" and not role_id:
            raise serializers.ValidationError({"role_id": Errors.ROLE_REQUIRED_FOR_APPROVAL})

        # Игнорируем роль при отклонении — она не имеет смысла
        if status == "отклонён" and role_id:
            attrs.pop("role_id", None)

        return attrs

    def update(self, instance: Application, validated_data: dict[str, Any]) -> Application:
        """Обработка заявки: одобрить -> создать пользователя, отклонить -> зафиксировать"""
        status = validated_data.get("status")
        review_comment = validated_data.get("review_comment")
        role_id = validated_data.get("role_id")

        request = self.context.get("request")

        if status == "предоставлен" and role_id:
            try:
                role = UserRole.objects.get(pk=role_id)
            except UserRole.DoesNotExist:
                raise serializers.ValidationError({"role_id": Errors.ROLE_NOT_FOUND}) from None

            user, created = UserAccount.objects.get_or_create(
                email=instance.email,
                defaults={
                    "role": role,
                    "password_hash": instance.password_hash,
                    "is_active": True,
                },
            )

            if not created:
                raise serializers.ValidationError({"email": Errors.EMAIL_REGISTERED})

            self.user_id = user.user_id

        instance.status = status
        instance.review_comment = review_comment
        instance.reviewed_by = getattr(request, "user", None)
        instance.save(update_fields=["status", "review_comment", "reviewed_by", "updated_at"])

        return instance

    def to_representation(self, instance: Application) -> dict[str, Any]:
        """Отправка ответа в таком формате"""
        result = "одобрена" if instance.status == "предоставлен" else "отклонена"
        data: dict[str, Any] = {"message": Messages.APPLICATION_REVIEWED.format(result=result)}

        if hasattr(self, "user_id"):
            data["user_id"] = self.user_id

        return data


# =============================================================================
# Логин
# =============================================================================


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Проверка данных, а после получение JWT токенов"""
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password", "")

        if not email or not password:
            raise serializers.ValidationError(Errors.INVALID_CREDENTIALS)

        request: Request | None = self.context.get("request")

        try:
            # Проверяем пользовательские данные
            user = (
                UserAccount.objects.select_related("role")
                .only("user_id", "email", "password_hash", "is_active", "last_login", "role__name")
                .get(email=email)
            )

            if not user.is_active:
                logger.warning(f"Попытка входа заблокированного пользователя: {email}")
                raise serializers.ValidationError(Errors.ACCOUNT_BLOCKED)

            if not user.check_password(password):
                logger.warning(f"Неудачная попытка входа: {email}")
                raise serializers.ValidationError(Errors.INVALID_CREDENTIALS)

        except UserAccount.DoesNotExist:
            logger.warning("Попытка входа с несуществующим email")
            raise serializers.ValidationError(Errors.INVALID_CREDENTIALS) from None

        # Получаем токены и обновляем последний вход
        jwt_manager = JWTManager()
        tokens = jwt_manager.create_tokens_for_user(user, request)  # type: ignore[arg-type]

        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "updated_at"])

        return tokens


# =============================================================================
# Пользователи
# =============================================================================


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = UserAccount
        fields = (
            "user_id",
            "email",
            "role_name",
            "last_login",
            "is_active",
            "created_at",
            "updated_at",
            "password_changed_at",
        )
        read_only_fields = fields


class ProfileUpdateSerializer(FlexibleModelSerializer):
    """Сериализатор для обновления профиля пользователем"""

    class Meta:
        model = UserAccount
        fields = ("email",)
        extra_kwargs: dict[str, Any] = {
            "email": {
                "error_messages": get_field_error_messages(UserAccount, "email"),
            },
        }

    def update(self, instance: UserAccount, validated_data: dict[str, Any]) -> UserAccount:
        """Обновляем данные и удаляем из кэша"""
        instance = super().update(instance, validated_data)
        UserService.invalidate_cache(instance.user_id)
        return instance


class UserUpdateSerializer(FlexibleModelSerializer):
    """Сериализатор для обновления пользователя администратором"""

    password = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={
            "blank": "Пароль не может быть пустым",
        },
    )

    class Meta:
        model = UserAccount
        fields = (
            "email",
            "role",
            "is_active",
            "password",
        )
        extra_kwargs: dict[str, Any] = {
            "email": {
                "error_messages": get_field_error_messages(UserAccount, "email"),
            },
            "role": {
                "error_messages": get_field_error_messages(UserAccount, "role"),
            },
            "is_active": {
                "error_messages": get_field_error_messages(UserAccount, "is_active"),
            },
        }

    def validate_password(self, value: str) -> str:
        """Валидация нового пароля"""
        password = value.strip()
        if not password:
            return value

        # Проверка через встроенные валидаторы Django
        request: Request = self.context.get("request")  # type: ignore[assignment]
        user = cast(UserAccount, request.user)

        password_validation.validate_password(password, user=user)  # type: ignore[arg-type]

        return password

    def update(self, instance: UserAccount, validated_data: dict[str, Any]) -> UserAccount:
        """Обновляем данные и удаляем из кэша"""
        request = self.context.get("request")
        if request is None or not isinstance(request.user, UserAccount):
            raise exceptions.PermissionDenied(Errors.CANNOT_ACT_ON_SELF)

        if instance.user_id == request.user.user_id:
            raise exceptions.PermissionDenied(Errors.CANNOT_ACT_ON_SELF)

        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            jwt_manager = JWTManager()
            jwt_manager.revoke_all_user_sessions(
                instance.user_id, reason=RevokeReasons.PASSWORD_CHANGED
            )
        UserService.invalidate_cache(instance.user_id)

        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Смена пароля пользователя"""

    old_password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "Заполните текущий пароль",
            "blank": "Текущий пароль не может быть пустым",
        },
    )
    new_password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "Заполните новый пароль",
            "blank": "Новый пароль не может быть пустым",
        },
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": "Заполните подтверждение пароля",
            "blank": "Подтверждение пароля не может быть пустым",
        },
    )

    def validate_old_password(self, value: str) -> str:
        """Проверка старого пароля"""
        old_password = value.strip()
        request = self.context.get("request")
        if request is None or not isinstance(request.user, UserAccount):
            raise exceptions.PermissionDenied("Требуется авторизация")

        if not request.user.check_password(old_password):
            raise ValidationError(Errors.INVALID_PASSWORD)

        return old_password

    def validate_new_password(self, value: str) -> str:
        """Валидация нового пароля"""
        password = value.strip()

        # Проверка через встроенные валидаторы Django
        request: Request = self.context.get("request")  # type: ignore[assignment]
        user = cast(UserAccount, request.user)

        password_validation.validate_password(password, user=user)  # type: ignore[arg-type]

        return password

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Общая валидация: совпадение паролей и новый пароль должен отличаться от старого"""
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": Errors.PASSWORDS_MISMATCH})

        old_password = attrs.get("old_password")

        if old_password == new_password:
            raise ValidationError({"new_password": Errors.PASSWORD_DIFFERENT})

        return attrs

    def save(self, **kwargs) -> None:
        """
        Сохранение нового пароля с автоматическим выходом со всех устройств,
        кроме текущего
        """
        request: Request = self.context.get("request")  # type: ignore[assignment]
        user = cast(UserAccount, request.user)
        current_jti = request.auth.payload.get("jti", "")  # type: ignore[union-attr]

        # Устанавливаем пароль
        new_password = self.validated_data.get("new_password")
        user.set_password(new_password)

        # Инвалидация кэша
        UserService.invalidate_cache(user.user_id)

        # Выходим со всех устройств, кроме текущего
        jwt_manager = JWTManager()
        jwt_manager.revoke_other_user_sessions(
            user.user_id, current_jti, reason=RevokeReasons.PASSWORD_CHANGED
        )
        logger.debug(f"{user.email} сменил пароль")


# =============================================================================
# Настройки системы
# =============================================================================


class CodeVerifySerializer(serializers.Serializer):
    """
    Сериализатор для проверки кода доступа.
    Используется на первом этапе регистрации.
    """

    code = serializers.CharField(
        validators=[validate_registration_code],
        error_messages={
            "required": "Заполните код доступа",
            "blank": "Код доступа не может быть пустым",
        },
    )


class SettingSerializer(serializers.Serializer):
    """Универсальный сериализатор для настроек"""

    value = serializers.CharField(
        error_messages={
            "required": "Заполните значение настройки",
            "blank": "Значение настройки не может быть пустым",
        }
    )

    @property
    def setting_key(self) -> str | None:
        return self.context.get("setting_key")

    def validate_value(self, value: str) -> str:
        value = value.strip()
        validators = {
            "registration_code": self._validate_code,
            "monitoring_years": self._validate_years,
            "cleanup_days": self._validate_days,
            "audit_log_retention_days": self._validate_audit_retention,
        }
        validator = validators.get(self.setting_key) if self.setting_key else None
        return validator(value) if validator else value

    def _validate_code(self, value: str) -> str:
        """Валидация кода регистрации"""
        if not 6 <= len(value) <= 24:
            raise ValidationError(Errors.CODE_LENGTH)
        return value

    def _validate_years(self, value: str) -> str:
        """Валидация периода мониторинга"""
        if not re.match(r"^\d{4}-\d{4}$", value):
            raise ValidationError(Errors.MONITORING_YEARS_FORMAT)
        start, end = map(int, value.split("-"))
        if start >= end:
            raise ValidationError(Errors.MONITORING_YEARS_ORDER)
        return value

    def _validate_days(self, value: str) -> str:
        """Валидация дней очистки заявок (минимум 1)"""
        if not value.isdigit() or int(value) < 1:
            raise ValidationError(Errors.CLEANUP_DAYS_INVALID)
        return value

    def _validate_audit_retention(self, value: str) -> str:
        """Валидация дней хранения логов аудита (минимум 30)"""
        if not value.isdigit() or int(value) < 30:
            raise ValidationError(Errors.AUDIT_RETENTION_DAYS_INVALID)
        return value


# =============================================================================
# Аудит
# =============================================================================


class AuditLogSerializer(serializers.ModelSerializer):
    """Сериализатор для логов аудита"""

    user_email = serializers.EmailField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "log_id",
            "timestamp",
            "user_id",
            "user_email",
            "action",
            "model_name",
            "object_id",
            "request_data",
            "old_values",
            "new_values",
            "ip_address",
        )
        read_only_fields = fields


# =============================================================================
# Сессии
# =============================================================================


class RevokeByFingerprintSerializer(serializers.Serializer):
    """Сериализатор для отзыва сессий по fingerprint"""

    fingerprint = serializers.CharField(
        required=True,
        write_only=True,
        error_messages={
            "required": "Укажите 'Отпечаток'",
            "blank": "'Отпечаток' не может быть пустым",
        },
    )
    user_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
        error_messages={
            "invalid": "Введите корректный ID пользователя",
        },
    )
    exclude_jti = serializers.CharField(required=False, allow_blank=True, write_only=True)


class RevokeAllUserSessionsSerializer(serializers.Serializer):
    """Сериализатор для отзыва всех сессий пользователя"""

    user_id = serializers.IntegerField(
        required=True,
        write_only=True,
        error_messages={
            "required": "Укажите ID пользователя",
            "invalid": "Введите корректный ID пользователя",
        },
    )
    exclude_jti = serializers.CharField(
        required=False, allow_blank=True, default="", write_only=True
    )
