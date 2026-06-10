import logging
from collections.abc import Callable
from datetime import date
from functools import wraps
from typing import Any

from django.db import models
from django.db.models import (
    Func,
    Value,
)
from ipware import get_client_ip
from rest_framework import permissions
from rest_framework.request import Request

from apps.account.models import AuditLog

logger = logging.getLogger(__name__)

DEFAULT_SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "old_password",
    "new_password",
    "current_password",
    "confirm_password",
    "token",
    "access_token",
    "refresh_token",
}


def get_instance_pk(instance) -> int | None:
    """Получить primary key из экземпляра модели Django"""
    if instance is None or not hasattr(instance, "_meta"):
        return None
    pk_field = instance._meta.pk.attname
    return getattr(instance, pk_field, None)


def sanitize_data(data: dict | None, sensitive_fields: set[str] | None = None) -> dict | None:
    """Скрывает чувствительные поля в словаре"""
    if data is None:
        return None

    fields = sensitive_fields or DEFAULT_SENSITIVE_FIELDS
    sanitized = {}

    for key, value in data.items():
        # Пропускаем файлы — они не JSON-сериализуемы
        if hasattr(value, "name") and hasattr(value, "size"):
            sanitized[key] = f"<File: {value.name}>"
            continue
        # Конвертируем date/datetime в строки
        if isinstance(value, date):
            sanitized[key] = value.isoformat()
            continue
        if key in fields:
            sanitized[key] = "***"
        else:
            sanitized[key] = value

    return sanitized if sanitized else None


def log_action(
    user_id: int | None,
    action: str,
    model: str,
    object_id: int | None = None,
    request_data: dict | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    request: Request | None = None,
):
    """
    Args:
    user_id: ID пользователя
    action: Действие (вход, создание, обновление, удаление, рассмотрение)
    model: Модель (Пользователь, Заявка, Настройка)
    object_id: ID объекта
    request_data: Данные запроса
    old_values: Старые значения (для update/delete)
    new_values: Новые значения (для create/update)
    request: Request для получения IP
    """
    ip_address = get_client_ip(request)[0] if request else None

    AuditLog.objects.create(
        user_id=user_id,
        action=action,
        model_name=model,
        object_id=object_id,
        request_data=request_data,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
    )


def audit_log(
    action: str,
    model: str,
    model_class: type[models.Model] | None = None,
    get_object_id: Callable[[dict], int | None] | None = None,
    get_old_values: Callable[[Request], dict | None] | None = None,
    get_new_values: Callable[[Request, dict], dict | None] | None = None,
    get_user_id: Callable[[dict], int | None] | None = None,
    sensitive_fields: set[str] | None = None,
    allowed_get: bool = False,
):
    """
    Декоратор для логирования действий в AuditLog.

    Args:
        action: Что сделано (вход, создание, обновление, удаление, рассмотрение)
        model: Имя модели (Пользователь, Заявка, Настройка)
        get_object_id: Функция для получения ID объекта из response data или request._audit_instance
        get_old_values: Функция для получения старых значений
        get_new_values: Функция для получения новых значений
        get_user_id: Функция для получения ID пользователя из request
        sensitive_fields: Поля для скрытия в логах (по умолчанию password, token, и т.д.),
        allowed_get: Разрешить метод GET-запросы (по умолчанию выключено логирование GET)
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(view: Any, request: Request, *args, **kwargs) -> Any:
            response = view_func(view, request, *args, **kwargs)

            # Логируем только успешные запросы
            if (
                hasattr(response, "status_code")
                and response.status_code < 400
                and (
                    request.method not in permissions.SAFE_METHODS
                    or (allowed_get and request.method == "GET")
                )
            ):
                data = response.data if hasattr(response, "data") else {}

                object_id = None

                if get_object_id and data:
                    object_id = get_object_id(data)

                # 1. Для create/update: берём pk из созданного/обновлённого объекта
                if object_id is None and hasattr(request, "_audit_instance"):
                    object_id = get_instance_pk(request._audit_instance)

                # 2. Для destroy/update: берём pk из сохранённых данных
                if object_id is None and hasattr(request, "_audit_old_data"):
                    old_data = request._audit_old_data
                    if model_class:
                        pk_field = model_class._meta.pk.name
                        object_id = old_data.get(pk_field)

                # 3. Для destroy: если нет данных, берём из URL
                if object_id is None and hasattr(view, "kwargs"):
                    object_id = view.kwargs.get("pk")

                # Старые данные
                old_values = None
                if get_old_values:
                    old_values = get_old_values(request)

                # Новые данные
                new_values = None
                if get_new_values:
                    new_values = get_new_values(request, data)

                # ID пользователя
                user_id = get_user_id(data) if get_user_id else None
                if user_id is None and hasattr(request.user, "user_id"):
                    user_id = request.user.user_id

                # Скрываем чувствительные данные
                request_data = sanitize_data(request.data, sensitive_fields)
                old_values_clean = sanitize_data(old_values, sensitive_fields)
                new_values_clean = sanitize_data(new_values, sensitive_fields)

                log_action(
                    user_id=user_id,
                    action=action,
                    model=model,
                    object_id=object_id,
                    request_data=request_data,
                    old_values=old_values_clean,
                    new_values=new_values_clean,
                    request=request,
                )

            return response

        return wrapper

    return decorator


class ConcatWS(Func):
    """Функция для объединения строк"""

    function = "CONCAT_WS"
    template = "%(function)s(%(expressions)s)"
    arg_joiner = ", "

    def __init__(self, separator, *expressions, **extra):
        expressions = (Value(separator),) + expressions
        super().__init__(*expressions, **extra)
