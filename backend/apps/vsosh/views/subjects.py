import logging
from typing import Any

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request

from apps.common.utils import audit_log

from ..cache_service import VSOSHCacheService
from ..constants import Limits
from ..models import Subject
from ..serializers.subjects import SubjectSerializer
from .base import BaseVSOSHViewSet, _generate_unique_short_name, _get_old_values

logger = logging.getLogger(__name__)


# =============================================================================
# Предметы
# =============================================================================


class SubjectViewSet(BaseVSOSHViewSet):
    """Управление предметами"""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["full_name", "short_name"]
    ordering_fields = ["subject_id", "full_name", "short_name"]
    ordering = ["full_name"]

    export_columns_map = {
        "subject_id": "ID",
        "full_name": "Полное название",
        "short_name": "Краткое название",
    }

    import_required_fields = ["full_name"]

    column_mapping = {
        "Полное название": "full_name",
        "Предмет": "full_name",
        "Краткое название": "short_name",
    }

    def _parse_import_row(self, row_data: dict[str, Any], row_num: int) -> dict[str, Any]:
        """Парсинг строки импорта для предмета"""
        self._validate_row(
            row_data,
            {"full_name": Limits.SUBJECT_FULL_NAME, "short_name": Limits.SUBJECT_SHORT_NAME},
            row_num,
        )
        full_name = self._get_resolved_value(row_data, "full_name")
        short_name = self._get_resolved_value(row_data, "short_name")

        return {"full_name": full_name, "short_name": short_name, "row_num": row_num}

    def _bulk_process(self, rows_data: list[dict[str, Any]], *args) -> tuple[int, int]:
        """Пакетная обработка предметов"""
        # === Этап 1: Загрузка существующих предметов ===
        existing_subjects = list(Subject.objects.all())
        existing_map = {s.full_name.lower(): s for s in existing_subjects}
        existing_short_names = {s.short_name.lower() for s in existing_subjects}

        to_create: list[Subject] = []
        to_update: list[Subject] = []

        # === Этап 2: Разделение на создание и обновление ===
        for row in rows_data:
            full_name = row["full_name"]
            short_name = row["short_name"]
            full_name_lower = full_name.lower()

            if full_name_lower in existing_map:
                instance = existing_map[full_name_lower]
                needs_update = False
                if instance.full_name != full_name:
                    instance.full_name = full_name
                    needs_update = True
                if short_name and instance.short_name != short_name:
                    instance.short_name = short_name
                    needs_update = True
                if needs_update:
                    to_update.append(instance)
            else:
                if not short_name:
                    short_name = _generate_unique_short_name(
                        full_name, Limits.SUBJECT_SHORT_NAME, existing_short_names
                    )
                    existing_short_names.add(short_name.lower())
                to_create.append(
                    Subject(
                        full_name=full_name,
                        short_name=short_name,
                    )
                )

        # === Этап 3: Запись в БД ===
        if to_create:
            Subject.objects.bulk_create(to_create, ignore_conflicts=True)
        if to_update:
            Subject.objects.bulk_update(to_update, ["full_name", "short_name"])

        return len(to_create), len(to_update)

    @audit_log(action="создание", model="Предмет", model_class=Subject)
    def create(self, request: Request, *args, **kwargs):
        """Создание нового предмета"""
        response = super().create(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="обновление",
        model="Предмет",
        model_class=Subject,
        get_old_values=_get_old_values,
    )
    def update(self, request: Request, *args, **kwargs):
        """Полное обновление предмета"""
        response = super().update(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="обновление",
        model="Предмет",
        model_class=Subject,
        get_old_values=_get_old_values,
    )
    def partial_update(self, request: Request, *args, **kwargs):
        """Частичное обновление предмета"""
        response = super().partial_update(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="удаление",
        model="Предмет",
        model_class=Subject,
        get_old_values=_get_old_values,
    )
    def destroy(self, request: Request, *args, **kwargs):
        """Удаление предмета"""
        response = super().destroy(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response
