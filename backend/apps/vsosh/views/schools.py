import logging
from difflib import get_close_matches
from typing import Any

from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from apps.common.utils import audit_log

from ..cache_service import VSOSHCacheService
from ..constants import Errors, Limits
from ..filters import EducationInstitutionFilter
from ..models import EducationInstitution, Municipality
from ..serializers.schools import EducationInstitutionSerializer
from .base import (
    BaseVSOSHViewSet,
    _generate_unique_short_name,
    _get_old_values,
    _load_municipalities,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Образовательные учреждения
# =============================================================================


class EducationInstitutionViewSet(BaseVSOSHViewSet):
    """Управление образовательными учреждениями"""

    serializer_class = EducationInstitutionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EducationInstitutionFilter
    search_fields = ["full_name", "short_name"]
    ordering_fields = ["institution_id", "full_name", "short_name", "municipality_name"]
    ordering = ["full_name"]

    export_columns_map = {
        "institution_id": "ID",
        "municipality_name": "Муниципалитет",
        "full_name": "Полное наименование ОУ",
        "short_name": "Краткое наименование ОУ",
    }

    import_required_fields = ["municipality_name", "full_name"]

    column_mapping = {
        "Муниципалитет": "municipality_name",
        "Полное наименование общеобразовательной организации": "full_name",
        "Полное наименование ОУ": "full_name",
        "Полное название общеобразовательной организации": "full_name",
        "Полное название ОУ": "full_name",
        "ОУ": "full_name",
        "Краткое наименование ОУ": "short_name",
        "Краткое название ОУ": "short_name",
    }

    def get_queryset(self):
        return EducationInstitution.objects.annotate(municipality_name=F("municipality__name"))

    def _parse_import_row(self, row_data: dict[str, Any], row_num: int) -> dict[str, Any]:
        """Парсинг строки импорта для образовательного учреждения"""
        self._validate_row(
            row_data,
            {
                "municipality_name": Limits.NAME,
                "full_name": Limits.INSTITUTION_FULL_NAME,
                "short_name": Limits.INSTITUTION_SHORT_NAME,
            },
            row_num,
        )

        municipality_name = self._get_resolved_value(row_data, "municipality_name")
        full_name = self._get_resolved_value(row_data, "full_name")
        short_name = self._get_resolved_value(row_data, "short_name")

        return {
            "municipality_name": municipality_name,
            "full_name": full_name,
            "short_name": short_name,
            "row_num": row_num,
        }

    def _validate_fk(
        self, rows_data: list[dict[str, Any]], error_details: list
    ) -> tuple[int, dict[str, Municipality]]:
        """Валидация FK: муниципалитет"""
        error_count = 0

        # Загрузка всех муниципалитетов одним запросом
        municipality_names = {row["municipality_name"] for row in rows_data}
        municipality_map = _load_municipalities(municipality_names)
        all_municipality_names = list(Municipality.objects.values_list("name", flat=True))

        for row in rows_data:
            mun_lower = row["municipality_name"].lower()
            if mun_lower not in municipality_map:
                matches = get_close_matches(
                    row["municipality_name"], all_municipality_names, n=1, cutoff=0.6
                )
                if matches:
                    error_msg = Errors.SUGGEST_DID_YOU_MEAN.format(
                        row_num=row["row_num"],
                        name=row["municipality_name"],
                        suggestion=matches[0],
                    )
                else:
                    error_msg = Errors.SUGGEST_ADD_TO_DIR.format(
                        row_num=row["row_num"],
                        name=row["municipality_name"],
                    )
                error_count += 1
                error_details.append({"row": row["row_num"], "error": error_msg})
            else:
                row["municipality"] = municipality_map[mun_lower]

        return error_count, municipality_map

    def _bulk_process(
        self,
        rows_data: list[dict[str, Any]],
        *args,
    ) -> tuple[int, int]:
        """Пакетная обработка образовательных учреждений"""
        # === Этап 1: Загрузка существующих учреждений ===
        existing_qs = EducationInstitution.objects.select_related("municipality").all()
        existing_map = {
            (inst.municipality_id, inst.full_name.lower()): {
                "id": inst.institution_id,
                "full_name": inst.full_name,
                "short_name": inst.short_name,
                "municipality_id": inst.municipality_id,
            }
            for inst in existing_qs
        }
        existing_short_names = {
            (inst.municipality_id, inst.short_name.lower()) for inst in existing_qs
        }

        to_create: list[EducationInstitution] = []
        to_update: list[EducationInstitution] = []

        # === Этап 2: Разделение на создание и обновление ===
        for row in rows_data:
            municipality = row.get("municipality")
            if not municipality:
                continue

            key = (municipality.municipality_id, row["full_name"].lower())
            mun_id = municipality.municipality_id

            if key in existing_map:
                inst_data = existing_map[key]
                needs_update = False

                if inst_data["short_name"] != row["short_name"]:
                    inst_data["short_name"] = row["short_name"]
                    needs_update = True
                if inst_data["full_name"] != row["full_name"]:
                    inst_data["full_name"] = row["full_name"]
                    needs_update = True

                if needs_update:
                    instance = EducationInstitution(
                        institution_id=inst_data["id"],  # type: ignore[misc]
                        municipality_id=inst_data["municipality_id"],  # type: ignore[misc]
                        full_name=inst_data["full_name"],  # type: ignore[misc]
                        short_name=inst_data["short_name"],  # type: ignore[misc]
                    )
                    to_update.append(instance)
            else:
                short_name = (
                    row["short_name"]
                    if row["short_name"]
                    else _generate_unique_short_name(
                        row["full_name"],
                        Limits.INSTITUTION_SHORT_NAME,
                        {sn for _, sn in existing_short_names},
                    )
                )
                existing_short_names.add((mun_id, short_name.lower()))

                to_create.append(
                    EducationInstitution(
                        municipality=municipality,
                        full_name=row["full_name"],
                        short_name=short_name,
                    )
                )

        # === Этап 3: Запись в БД ===
        if to_create:
            EducationInstitution.objects.bulk_create(to_create, ignore_conflicts=True)
        if to_update:
            EducationInstitution.objects.bulk_update(to_update, ["full_name", "short_name"])

        return len(to_create), len(to_update)

    @audit_log(
        action="создание",
        model="Образовательное учреждение",
        model_class=EducationInstitution,
    )
    def create(self, request: Request, *args, **kwargs):
        """Создание нового образовательного учреждения"""
        response = super().create(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="обновление",
        model="Образовательное учреждение",
        model_class=EducationInstitution,
        get_old_values=_get_old_values,
    )
    def update(self, request: Request, *args, **kwargs):
        """Полное обновление образовательного учреждения"""
        response = super().update(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="обновление",
        model="Образовательное учреждение",
        model_class=EducationInstitution,
        get_old_values=_get_old_values,
    )
    def partial_update(self, request: Request, *args, **kwargs):
        """Частичное обновление образовательного учреждения"""
        response = super().partial_update(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="удаление",
        model="Образовательное учреждение",
        model_class=EducationInstitution,
        get_old_values=_get_old_values,
    )
    def destroy(self, request: Request, *args, **kwargs):
        """Удаление образовательного учреждения"""
        response = super().destroy(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @action(detail=False, methods=["get"], url_path="filters")
    def get_filters(self, request: Request) -> Response:
        """Получить значения для фильтров образовательных учреждений"""
        cached = VSOSHCacheService.get_filters()
        if cached and "municipalities" in cached:
            return Response({"municipalities": cached["municipalities"]})

        municipalities = list(
            Municipality.objects.values("municipality_id", "name").distinct().order_by("name")
        )
        return Response({"municipalities": municipalities})
