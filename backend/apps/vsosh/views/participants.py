import logging
from datetime import date
from typing import Any

from django.db.models import CharField, F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from apps.common.utils import ConcatWS, audit_log

from ..constants import Errors, Limits
from ..filters import ParticipantFilter
from ..models import Participant
from ..queries import search_participants
from ..serializers.participants import ParticipantSearchSerializer, ParticipantSerializer
from .base import (
    BaseVSOSHViewSet,
    _get_old_values,
    _parse_gender,
    parse_russian_date,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Участники
# =============================================================================


class ParticipantViewSet(BaseVSOSHViewSet):
    """Управление участниками"""

    serializer_class = ParticipantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ParticipantFilter
    search_fields = ["lastname", "firstname", "patronymic", "birth_date"]
    ordering_fields = [
        "participant_id",
        "lastname",
        "firstname",
        "patronymic",
        "birth_date",
        "gender",
        "full_name",
    ]
    ordering = ["full_name"]

    def get_queryset(self):
        return Participant.objects.annotate(
            full_name=ConcatWS(
                " ",
                F("lastname"),
                F("firstname"),
                F("patronymic"),
                output_field=CharField(),
            )
        ).all()

    export_columns_map = {
        "participant_id": "ID",
        "lastname": "Фамилия",
        "firstname": "Имя",
        "patronymic": "Отчество",
        "full_name": "ФИО",
        "birth_date": "Дата рождения",
        "gender": "Пол",
    }

    import_required_fields = ["lastname", "firstname", "birth_date", "gender"]

    column_mapping = {
        "Фамилия": "lastname",
        "Имя": "firstname",
        "Отчество": "patronymic",
        "Пол": "gender",
        "Дата рождения": "birth_date",
    }

    def _parse_import_row(self, row_data: dict[str, Any], row_num: int) -> dict[str, Any]:
        """Парсинг строки импорта для участника"""
        self._validate_row(
            row_data,
            {"lastname": Limits.NAME, "firstname": Limits.NAME, "patronymic": Limits.NAME},
            row_num,
        )
        birth_date_raw = self._get_resolved_value(row_data, "birth_date")
        gender_raw = self._get_resolved_value(row_data, "gender")

        # === Другие проверки ===
        gender = _parse_gender(gender_raw, row_num)

        birth_date = parse_russian_date(birth_date_raw)
        if birth_date.year < Limits.BIRTH_DATE_MIN_YEAR or birth_date > date.today():
            raise ValueError(
                Errors.IMPORT_BIRTH_DATE_INVALID.format(
                    row_num=row_num, min_year=Limits.BIRTH_DATE_MIN_YEAR
                )
            )

        # === Извлечение данных ===
        lastname = self._get_resolved_value(row_data, "lastname")
        firstname = self._get_resolved_value(row_data, "firstname")
        patronymic = self._get_resolved_value(row_data, "patronymic") or None

        return {
            "lastname": lastname,
            "firstname": firstname,
            "patronymic": patronymic,
            "birth_date": birth_date,
            "gender": gender,
            "row_num": row_num,
        }

    def _bulk_process(self, rows_data: list[dict[str, Any]], *args) -> tuple[int, int]:
        """Пакетная обработка участников"""
        # === Этап 1: Загрузка существующих участников ===
        existing_qs = Participant.objects.all()
        existing_map = {
            (p.lastname, p.firstname, p.patronymic, p.birth_date): p for p in existing_qs
        }

        to_create: list[Participant] = []
        to_update: list[Participant] = []

        # === Этап 2: Разделение на создание и обновление ===
        for row in rows_data:
            key = (row["lastname"], row["firstname"], row["patronymic"], row["birth_date"])

            if key in existing_map:
                instance = existing_map[key]
                if instance.gender != row["gender"]:
                    instance.gender = row["gender"]
                    to_update.append(instance)
            else:
                to_create.append(
                    Participant(
                        lastname=row["lastname"],
                        firstname=row["firstname"],
                        patronymic=row["patronymic"],
                        birth_date=row["birth_date"],
                        gender=row["gender"],
                    )
                )

        # === Этап 3: Запись в БД ===
        if to_create:
            Participant.objects.bulk_create(to_create, ignore_conflicts=True)
        if to_update:
            Participant.objects.bulk_update(to_update, ["gender"])

        return len(to_create), len(to_update)

    @audit_log(action="создание", model="Участник", model_class=Participant)
    def create(self, request: Request, *args, **kwargs):
        """Создание нового участника"""
        return super().create(request, *args, **kwargs)

    @audit_log(
        action="обновление",
        model="Участник",
        model_class=Participant,
        get_old_values=_get_old_values,
    )
    def update(self, request: Request, *args, **kwargs):
        """Полное обновление участника"""
        return super().update(request, *args, **kwargs)

    @audit_log(
        action="обновление",
        model="Участник",
        model_class=Participant,
        get_old_values=_get_old_values,
    )
    def partial_update(self, request: Request, *args, **kwargs):
        """Частичное обновление участника"""
        return super().partial_update(request, *args, **kwargs)

    @audit_log(
        action="удаление",
        model="Участник",
        model_class=Participant,
        get_old_values=_get_old_values,
    )
    def destroy(self, request: Request, *args, **kwargs):
        """Удаление участника"""
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """
        Поиск участников для селектов и дашборда.
        Пример: /vsosh/participants/search/?q=Иванов&limit=20&offset=20
        """
        serializer = ParticipantSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = search_participants(
            q=serializer.validated_data["q"],
            limit=serializer.validated_data["limit"],
            offset=serializer.validated_data["offset"],
        )
        return Response(data)
