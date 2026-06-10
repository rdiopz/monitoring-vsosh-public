import logging
from datetime import timedelta

from celery import shared_task  # type: ignore[import-untyped]
from django.utils import timezone

from .jwt_sessions import SessionStorage
from .models import Application, AuditLog, SystemSetting

logger = logging.getLogger(__name__)


@shared_task  # type: ignore[misc]
def cleanup_stale_jti() -> dict[str, int]:
    """Чистит мёртвые JTI из индексов u: и f:"""
    storage = SessionStorage()

    removed_from_u = storage.cleanup_index("u:*")
    removed_from_f = storage.cleanup_index("f:*")

    logger.info(f"Очищено мёртвых JTI: u:{removed_from_u}, f:{removed_from_f}")
    return {"removed_from_u": removed_from_u, "removed_from_f": removed_from_f}


@shared_task  # type: ignore[misc]
def cleanup_applications() -> dict[str, int]:
    """Очищает отклонённые заявки старше указанного в настройках количества дней"""
    now = timezone.now()

    days_value = (
        SystemSetting.objects.filter(key="application_cleanup_days")
        .values_list("value", flat=True)
        .first()
    )
    days = int(days_value) if days_value else 3

    threshold = now - timedelta(days=days)
    deleted_rejected, _ = Application.objects.filter(
        status="отклонён", updated_at__lt=threshold
    ).delete()

    logger.info(f"Очистка заявок: удалено отклонённых={deleted_rejected}")

    return {"deleted_rejected": deleted_rejected}


@shared_task
def cleanup_audit_logs():
    """Удаляет логи аудита старше N дней (по умолчанию 90, минимум 30)."""
    try:
        setting = SystemSetting.objects.get(key="audit_log_retention_days")
        days = int(setting.value)
    except (SystemSetting.DoesNotExist, ValueError):
        days = 90

    if days < 30:
        days = 90

    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()

    logger.info(f"Очистка логов аудита: удалено {deleted_count} записей старше {days} дней")
    return deleted_count
