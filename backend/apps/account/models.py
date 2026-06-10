from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone

from apps.common.fields import PostgreSQLEnumField

from .constants import Errors


class AuditLog(models.Model):
    log_id = models.BigAutoField(primary_key=True, verbose_name="ID")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Время")
    user = models.ForeignKey(
        "UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Пользователь",
    )
    action = models.CharField(max_length=50, verbose_name="Действие")
    model_name = models.CharField(max_length=100, verbose_name="Модель")
    object_id = models.IntegerField(null=True, blank=True, verbose_name="ID объекта")
    request_data = models.JSONField(null=True, blank=True, verbose_name="Данные запроса")
    old_values = models.JSONField(null=True, blank=True, verbose_name="Старые значения")
    new_values = models.JSONField(null=True, blank=True, verbose_name="Новые значения")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")

    class Meta:
        db_table = "audit_log"
        verbose_name = "лог аудита"
        verbose_name_plural = "логи аудита"
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["model_name", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.action} — {self.model_name} ({self.timestamp})"


class UserRole(models.Model):
    role_id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(
        unique=True,
        max_length=50,
        verbose_name="Название",
        error_messages={"unique": Errors.USER_ROLE_EXISTS},
    )

    class Meta:
        db_table = "user_role"
        verbose_name = "роль пользователя"
        verbose_name_plural = "роли пользователей"

    def __str__(self):
        return self.name


class UserAccount(models.Model):
    user_id = models.AutoField(primary_key=True, verbose_name="ID")
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name="Email",
        error_messages={"unique": Errors.USER_EMAIL_EXISTS},
    )
    role = models.ForeignKey(
        UserRole,
        models.DO_NOTHING,
        db_column="role_id",
        verbose_name="Роль",
    )
    password_hash = models.CharField(max_length=100, verbose_name="Хеш пароля")
    last_login = models.DateTimeField(default=timezone.now, verbose_name="Последний вход")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")
    password_changed_at = models.DateTimeField(null=True, blank=True, verbose_name="Смена пароля")

    class Meta:
        db_table = "user_account"
        verbose_name = "учётная запись"
        verbose_name_plural = "учётные записи"
        indexes = [models.Index(fields=["email"])]

    def __str__(self):
        return self.email

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_password(self, raw_password: str):
        self.password_hash = make_password(raw_password)
        self.password_changed_at = timezone.now()
        self.save(update_fields=["password_hash", "password_changed_at", "updated_at"])

    def check_password(self, raw_password: str):
        return check_password(raw_password, self.password_hash)

    @property
    def days_since_password_change(self):
        if not self.password_changed_at:
            return None
        return (timezone.now() - self.password_changed_at).days


class SystemSetting(models.Model):
    setting_id = models.AutoField(primary_key=True, verbose_name="ID")
    key = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Ключ",
        error_messages={"unique": Errors.SYSTEM_SETTING_KEY_EXISTS},
    )
    value = models.CharField(max_length=255, verbose_name="Значение")
    description = models.CharField(max_length=300, verbose_name="Описание")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    updated_by = models.ForeignKey(
        UserAccount,
        models.SET_NULL,
        db_column="updated_by",
        blank=True,
        null=True,
        related_name="updated_settings",
        verbose_name="Обновил",
    )

    class Meta:
        db_table = "system_setting"
        verbose_name = "настройка системы"
        verbose_name_plural = "настройки системы"
        indexes = [
            models.Index(fields=["key"]),
        ]

    def __str__(self):
        return f"{self.key} = {self.value}"


class Application(models.Model):
    application_id = models.AutoField(primary_key=True, verbose_name="ID")
    email = models.EmailField(
        unique=True,
        max_length=255,
        verbose_name="Email",
        error_messages={"unique": Errors.APPLICATION_EMAIL_EXISTS},
    )
    password_hash = models.CharField(max_length=100, verbose_name="Хеш пароля")
    application_datetime = models.DateTimeField(default=timezone.now, verbose_name="Дата заявки")
    status = PostgreSQLEnumField(
        enum_type="application_status_type",
        enum_values=["предоставлен", "рассматривается", "отклонён"],
        default="рассматривается",
        verbose_name="Статус",
    )
    reviewed_by = models.ForeignKey(
        UserAccount,
        models.SET_NULL,
        db_column="reviewed_by",
        blank=True,
        null=True,
        related_name="reviewed_applications",
        verbose_name="Рассмотрел",
    )
    review_comment = models.CharField(
        max_length=500, blank=True, null=True, verbose_name="Комментарий"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "application"
        verbose_name = "заявка"
        verbose_name_plural = "заявки"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["application_datetime"]),
        ]

    def __str__(self):
        return f"{self.email} — {self.status}"
