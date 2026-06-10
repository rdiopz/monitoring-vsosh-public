import logging
from typing import Any

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request

from apps.common.utils import audit_log

from ..constants import Limits
from ..models import Municipality
from ..serializers.municipalities import MunicipalitySerializer
from .base import BaseVSOSHViewSet, _get_old_values

logger = logging.getLogger(__name__)


# =============================================================================
# Муниципалитет
# =============================================================================


class MunicipalityViewSet(BaseVSOSHViewSet):
    """Управление муниципалитетами"""

    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["municipality_id", "name"]
    ordering = ["name"]

    export_columns_map = {
        "municipality_id": "ID",
        "name": "Название",
    }

    import_required_fields = ["name"]

    column_mapping = {
        "Название": "name",
        "Муниципалитет": "name",
    }

    def _parse_import_row(self, row_data: dict[str, Any], row_num: int) -> dict[str, Any]:
        """Парсинг строки импорта для муниципалитета"""
        self._validate_row(row_data, {"name": Limits.NAME}, row_num)
        name = self._get_resolved_value(row_data, "name")
        return {"name": name, "row_num": row_num}

    def _bulk_process(self, rows_data: list[dict[str, Any]], *args) -> tuple[int, int]:
        """Пакетная обработка муниципалитетов"""
        # === Этап 1: Загрузка существующих муниципалитетов ===
        existing_map = {m.name.lower(): m for m in Municipality.objects.all()}

        to_create: list[Municipality] = []
        to_update: list[Municipality] = []

        # === Этап 2: Разделение на создание и обновление ===
        for row in rows_data:
            name = row["name"]
            name_lower = name.lower()

            if name_lower in existing_map:
                instance = existing_map[name_lower]
                if instance.name != name:
                    instance.name = name
                    to_update.append(instance)
            else:
                to_create.append(Municipality(name=name))

        # === Этап 3: Запись в БД ===
        if to_create:
            Municipality.objects.bulk_create(to_create, ignore_conflicts=True)
        if to_update:
            Municipality.objects.bulk_update(to_update, ["name"])

        return len(to_create), len(to_update)

    @audit_log(action="создание", model="Муниципалитет", model_class=Municipality)
    def create(self, request: Request, *args, **kwargs):
        """Создание нового муниципалитета"""
        return super().create(request, *args, **kwargs)

    @audit_log(
        action="обновление",
        model="Муниципалитет",
        model_class=Municipality,
        get_old_values=_get_old_values,
    )
    def update(self, request: Request, *args, **kwargs):
        """Полное обновление муниципалитета"""
        return super().update(request, *args, **kwargs)

    @audit_log(
        action="обновление",
        model="Муниципалитет",
        model_class=Municipality,
        get_old_values=_get_old_values,
    )
    def partial_update(self, request: Request, *args, **kwargs):
        """Частичное обновление муниципалитета"""
        return super().partial_update(request, *args, **kwargs)

    @audit_log(
        action="удаление",
        model="Муниципалитет",
        model_class=Municipality,
        get_old_values=_get_old_values,
    )
    def destroy(self, request: Request, *args, **kwargs):
        """Удаление муниципалитета"""
        return super().destroy(request, *args, **kwargs)
