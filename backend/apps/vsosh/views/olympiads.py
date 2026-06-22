import logging
from datetime import date
from difflib import get_close_matches
from typing import Any

from django.db.models import CharField, F, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response

from apps.common.utils import ConcatWS, audit_log

from ..cache_service import VSOSHCacheService
from ..constants import Errors, Limits
from ..filters import OlympiadParticipationFilter
from ..models import EducationInstitution, Municipality, OlympiadParticipation, Participant, Subject
from ..serializers.olympiads import (
    OlympiadParticipationCreateSerializer,
    OlympiadParticipationSerializer,
    OlympiadParticipationUpdateSerializer,
)
from .base import (
    BaseVSOSHViewSet,
    _get_old_values,
    _load_municipalities,
    _parse_gender,
    parse_russian_date,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Участия в олимпиаде
# =============================================================================


class OlympiadParticipationViewSet(BaseVSOSHViewSet):
    """Управление участиями в олимпиаде"""

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OlympiadParticipationFilter
    search_fields = [
        "participant__lastname",
        "participant__firstname",
        "participant__patronymic",
        "participant__birth_date",
        "education__full_name",
        "education__short_name",
        "subject__full_name",
        "subject__short_name",
    ]
    ordering_fields = [
        "olymp_id",
        "year",
        "class_field",
        "stage",
        "status",
        "participant_lastname",
        "participant_firstname",
        "participant_patronymic",
        "participant_birth_date",
        "participant_gender",
        "education_institution_name",
        "education_short_name",
        "municipality_name",
        "subject_full_name",
        "subject_short_name",
        "created_at",
        "updated_at",
    ]
    ordering = ["-year"]

    export_columns_map = {
        "olymp_id": "ID",
        "participant_full_name": "ФИО участника",
        "participant_lastname": "Фамилия",
        "participant_firstname": "Имя",
        "participant_patronymic": "Отчество",
        "participant_gender": "Пол",
        "participant_birth_date": "Дата рождения",
        "education_institution_name": "Полное наименование ОУ",
        "education_short_name": "Краткое наименование ОУ",
        "municipality_name": "Муниципалитет",
        "subject_full_name": "Предмет",
        "subject_short_name": "Краткое название предмета",
        "class_field": "Класс",
        "stage": "Этап",
        "status": "Статус",
        "year": "Год",
        "created_at": "Дата создания",
        "updated_at": "Дата обновления",
    }

    import_required_fields = [
        "participant_lastname",
        "participant_firstname",
        "participant_gender",
        "participant_birth_date",
        "municipality_name",
        "education_institution_name",
        "subject_full_name",
        "class_field",
        "stage",
        "status",
        "year",
    ]

    column_mapping = {
        "Фамилия": "participant_lastname",
        "Имя": "participant_firstname",
        "Отчество": "participant_patronymic",
        "Пол": "participant_gender",
        "Дата рождения": "participant_birth_date",
        "Муниципалитет": "municipality_name",
        "Полное наименование общеобразовательной организации": "education_institution_name",
        "Полное наименование ОУ": "education_institution_name",
        "Полное название общеобразовательной организации": "education_institution_name",
        "Полное название ОУ": "education_institution_name",
        "ОУ": "education_institution_name",
        "Предмет": "subject_full_name",
        "Класс": "class_field",
        "Класс обучения": "class_field",
        "Этап": "stage",
        "Статус участника": "status",
        "Статус": "status",
        "Год участия": "year",
        "Год": "year",
    }

    _serializers = {
        "create": OlympiadParticipationCreateSerializer,
        "update": OlympiadParticipationUpdateSerializer,
        "partial_update": OlympiadParticipationUpdateSerializer,
    }

    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор в зависимости от действия"""
        if self.action in ["list", "retrieve", "export"]:
            return OlympiadParticipationSerializer
        return self._serializers.get(self.action, OlympiadParticipationCreateSerializer)

    def get_queryset(self):
        """Возвращает queryset с оптимизацией запросов и аннотациями для сортировки"""
        queryset = OlympiadParticipation.objects.select_related(
            "participant",
            "education",
            "education__municipality",
            "subject",
        )

        if self.action in ["list", "retrieve", "export"]:
            return OlympiadParticipation.objects.annotate(
                participant_lastname=F("participant__lastname"),
                participant_firstname=F("participant__firstname"),
                participant_patronymic=F("participant__patronymic"),
                participant_birth_date=F("participant__birth_date"),
                participant_gender=F("participant__gender"),
                participant_full_name=ConcatWS(
                    " ",
                    F("participant__lastname"),
                    F("participant__firstname"),
                    F("participant__patronymic"),
                    output_field=CharField(),
                ),
                education_institution_name=F("education__full_name"),
                education_short_name=F("education__short_name"),
                municipality=F("education__municipality_id"),
                municipality_name=F("education__municipality__name"),
                subject_full_name=F("subject__full_name"),
                subject_short_name=F("subject__short_name"),
            ).all()

        return queryset.all()

    def filter_queryset(self, queryset):
        """Для update/partial_update пропускаем фильтрацию"""
        if self.action in ["update", "partial_update", "destroy"]:
            return queryset
        return super().filter_queryset(queryset)

    @audit_log(
        action="создание",
        model="Участие в олимпиаде",
        model_class=OlympiadParticipation,
    )
    def create(self, request: Request, *args, **kwargs):
        """Создание нового участия в олимпиаде"""
        response = super().create(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="обновление",
        model="Участие в олимпиаде",
        model_class=OlympiadParticipation,
        get_old_values=_get_old_values,
    )
    def update(self, request: Request, *args, **kwargs):
        """Полное обновление участия в олимпиаде"""
        response = super().update(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="обновление",
        model="Участие в олимпиаде",
        model_class=OlympiadParticipation,
        get_old_values=_get_old_values,
    )
    def partial_update(self, request: Request, *args, **kwargs):
        """Частичное обновление участия в олимпиаде"""
        response = super().partial_update(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    @audit_log(
        action="удаление",
        model="Участие в олимпиаде",
        model_class=OlympiadParticipation,
        get_old_values=_get_old_values,
    )
    def destroy(self, request: Request, *args, **kwargs):
        """Удаление участия в олимпиаде"""
        response = super().destroy(request, *args, **kwargs)
        VSOSHCacheService.invalidate_filters()
        return response

    def _parse_import_row(self, row_data: dict[str, Any], row_num: int) -> dict[str, Any]:
        """Парсинг строки импорта для участия в олимпиаде"""
        self._validate_row(
            row_data,
            {
                "participant_lastname": Limits.NAME,
                "participant_firstname": Limits.NAME,
                "participant_patronymic": Limits.NAME,
                "municipality_name": Limits.NAME,
                "education_institution_name": Limits.INSTITUTION_FULL_NAME,
                "subject_full_name": Limits.SUBJECT_FULL_NAME,
            },
            row_num,
        )

        # === Извлечение и валидация числовых/перечислимых полей ===
        class_field_raw = self._get_resolved_value(row_data, "class_field")
        if isinstance(class_field_raw, str) and class_field_raw.strip().isdigit():
            class_field = int(class_field_raw.strip())
        elif not isinstance(class_field_raw, int):
            class_field = None
        else:
            class_field = class_field_raw

        if (
            not isinstance(class_field, int)
            or class_field < Limits.CLASS_MIN
            or class_field > Limits.CLASS_MAX
        ):
            raise ValueError(
                Errors.IMPORT_CLASS_INVALID.format(
                    row_num=row_num, min=Limits.CLASS_MIN, max=Limits.CLASS_MAX
                )
            )

        year_raw = self._get_resolved_value(row_data, "year")
        if isinstance(year_raw, str) and year_raw.strip().isdigit():
            year = int(year_raw.strip())
        elif not isinstance(year_raw, int):
            year = None
        else:
            year = year_raw

        if not isinstance(year, int) or year < Limits.YEAR_MIN:
            raise ValueError(
                Errors.IMPORT_YEAR_INVALID.format(row_num=row_num, min_year=Limits.YEAR_MIN)
            )

        stage_raw = self._get_resolved_value(row_data, "stage")
        stage = stage_raw.strip() if isinstance(stage_raw, str) else str(stage_raw)
        if stage not in Limits.STAGE_VALUES:
            raise ValueError(
                Errors.IMPORT_STAGE_INVALID.format(
                    row_num=row_num, value=stage, allowed=", ".join(Limits.STAGE_VALUES)
                )
            )

        status_raw = self._get_resolved_value(row_data, "status")
        status = status_raw.strip() if isinstance(status_raw, str) else str(status_raw)
        if status not in Limits.STATUS_VALUES:
            raise ValueError(
                Errors.IMPORT_STATUS_INVALID.format(
                    row_num=row_num, value=status, allowed=", ".join(Limits.STATUS_VALUES)
                )
            )

        birth_date_raw = self._get_resolved_value(row_data, "participant_birth_date")
        birth_date = parse_russian_date(birth_date_raw)
        if birth_date.year < Limits.BIRTH_DATE_MIN_YEAR or birth_date > date.today():
            raise ValueError(
                Errors.IMPORT_BIRTH_DATE_INVALID.format(
                    row_num=row_num, min_year=Limits.BIRTH_DATE_MIN_YEAR
                )
            )

        gender_raw = self._get_resolved_value(row_data, "participant_gender")
        gender = _parse_gender(gender_raw, row_num)

        # === Извлечение текстовых полей ===
        lastname = self._get_resolved_value(row_data, "participant_lastname")
        firstname = self._get_resolved_value(row_data, "participant_firstname")
        patronymic = self._get_resolved_value(row_data, "participant_patronymic") or None
        municipality_name = self._get_resolved_value(row_data, "municipality_name")
        education_name = self._get_resolved_value(row_data, "education_institution_name")
        subject_name = self._get_resolved_value(row_data, "subject_full_name")

        return {
            "lastname": lastname.strip(),
            "firstname": firstname.strip(),
            "patronymic": patronymic.strip() if patronymic else None,
            "birth_date": birth_date,
            "gender": gender,
            "municipality_name": municipality_name.strip(),
            "education_name": education_name.strip(),
            "subject_name": subject_name.strip(),
            "class_field": class_field,
            "stage": stage,
            "status": status,
            "year": year,
            "row_num": row_num,
        }

    def _validate_fk(
        self, rows_data: list[dict[str, Any]], error_details: list
    ) -> tuple[int, dict, dict, dict]:
        """Валидация FK с проверкой и подсказками"""
        error_count = 0

        # === 1. Пакетная загрузка муниципалитетов ===
        municipality_names = {row["municipality_name"] for row in rows_data}
        municipalities = _load_municipalities(municipality_names)
        all_municipality_names = list(Municipality.objects.values_list("name", flat=True))

        # === 2. Пакетная загрузка существующих ОУ ===
        all_education = EducationInstitution.objects.select_related("municipality").all()
        education_by_mun_and_name: dict[tuple[int, str], EducationInstitution] = {
            (edu.municipality_id, edu.full_name.lower()): edu for edu in all_education
        }

        education_by_name: dict[str, list[EducationInstitution]] = {}
        for edu in all_education:
            name_lower = edu.full_name.lower()
            education_by_name.setdefault(name_lower, []).append(edu)

        # === 3. Группировка ОУ по муниципалитетам ===
        education_names_by_municipality: dict[int, list[str]] = {}
        for edu in all_education:
            education_names_by_municipality.setdefault(edu.municipality_id, []).append(
                edu.full_name
            )

        # === 4. Пакетная загрузка предметов ===
        all_subjects = Subject.objects.all()
        subjects_by_name = {s.full_name.lower(): s for s in all_subjects}
        all_subject_names = list(subjects_by_name.keys())

        # === 5. Кэши для валидных объектов ===
        education_cache: dict[tuple[int, str], EducationInstitution] = {}
        subject_cache: dict[str, Subject] = {}
        municipality_cache: dict[str, Municipality] = {}

        for row in rows_data:
            row_num = row["row_num"]
            mun_name = row["municipality_name"]
            mun_name_lower = mun_name.lower()

            # === Муниципалитет ===
            if mun_name_lower in municipalities:
                municipality = municipalities[mun_name_lower]
                municipality_cache[mun_name] = municipality
            else:
                matches = get_close_matches(mun_name, all_municipality_names, n=1, cutoff=0.6)
                error_msg = (
                    Errors.SUGGEST_DID_YOU_MEAN.format(
                        row_num=row_num, name=mun_name, suggestion=matches[0]
                    )
                    if matches
                    else Errors.SUGGEST_ADD_TO_DIR.format(row_num=row_num, name=mun_name)
                )
                error_count += 1
                error_details.append({"row": row_num, "error": error_msg})
                continue

            # === Образовательное учреждение ===
            edu_name = row["education_name"]
            edu_name_lower = edu_name.lower()
            edu_key = (municipality.municipality_id, edu_name_lower)

            if edu_key in education_by_mun_and_name:
                education_cache[edu_key] = education_by_mun_and_name[edu_key]
            else:
                same_name_other = [
                    e
                    for e in education_by_name.get(edu_name_lower, [])
                    if e.municipality_id != municipality.municipality_id
                ]

                if same_name_other:
                    error_msg = Errors.SUGGEST_WRONG_MUNICIPALITY.format(
                        row_num=row_num,
                        name=edu_name,
                        actual_municipality=same_name_other[0].municipality.name,
                        expected_municipality=municipality.name,
                    )
                else:
                    all_edu_names_in_mun = education_names_by_municipality.get(
                        municipality.municipality_id, []
                    )
                    matches = get_close_matches(edu_name, all_edu_names_in_mun, n=1, cutoff=0.7)
                    error_msg = (
                        Errors.SUGGEST_DID_YOU_MEAN.format(
                            row_num=row_num, name=edu_name, suggestion=matches[0]
                        )
                        if matches
                        else Errors.SUGGEST_IMPORT_REF.format(
                            row_num=row_num,
                            name=edu_name,
                            ref_name="образовательных учреждений",
                        )
                    )

                error_count += 1
                error_details.append({"row": row_num, "error": error_msg})
                continue

            # === Предмет ===
            subj_name = row["subject_name"]
            subj_name_lower = subj_name.lower()

            if subj_name_lower in subjects_by_name:
                subject_cache[subj_name] = subjects_by_name[subj_name_lower]
            else:
                matches = get_close_matches(subj_name_lower, all_subject_names, n=1, cutoff=0.7)
                error_msg = (
                    Errors.SUGGEST_DID_YOU_MEAN.format(
                        row_num=row_num, name=subj_name, suggestion=matches[0]
                    )
                    if matches
                    else Errors.SUGGEST_IMPORT_REF.format(
                        row_num=row_num,
                        name=subj_name,
                        ref_name="предметов",
                    )
                )
                error_count += 1
                error_details.append({"row": row_num, "error": error_msg})
                continue

        return error_count, education_cache, subject_cache, municipality_cache

    def _bulk_process(
        self,
        rows_data: list[dict[str, Any]],
        education_cache: dict | None = None,
        subject_cache: dict | None = None,
        municipality_cache: dict | None = None,
    ) -> tuple[int, int]:
        """Пакетная обработка участий в олимпиаде"""
        education_cache = education_cache or {}
        subject_cache = subject_cache or {}
        municipality_cache = municipality_cache or {}

        # === Этап 1: Поиск существующих участников ===
        participant_conditions = Q()
        for row in rows_data:
            if row["patronymic"]:
                participant_conditions |= Q(
                    lastname=row["lastname"],
                    firstname=row["firstname"],
                    patronymic=row["patronymic"],
                    birth_date=row["birth_date"],
                )
            else:
                participant_conditions |= Q(
                    lastname=row["lastname"],
                    firstname=row["firstname"],
                    patronymic__isnull=True,
                    birth_date=row["birth_date"],
                )

        def _participant_key(p: Participant) -> tuple[str, str, str | None, date]:
            return (p.lastname, p.firstname, p.patronymic, p.birth_date)

        def _row_key(row: dict[str, Any]) -> tuple[str, str, str | None, date]:
            return (row["lastname"], row["firstname"], row["patronymic"], row["birth_date"])

        existing_participants = {
            _participant_key(p): p for p in Participant.objects.filter(participant_conditions)
        }

        # === Этап 2: Создание недостающих участников ===
        to_create_participants = [
            Participant(
                lastname=row["lastname"],
                firstname=row["firstname"],
                patronymic=row["patronymic"],
                birth_date=row["birth_date"],
                gender=row["gender"],
            )
            for row in rows_data
            if _row_key(row) not in existing_participants
        ]

        if to_create_participants:
            Participant.objects.bulk_create(to_create_participants, ignore_conflicts=True)

            existing_participants = {
                _participant_key(p): p for p in Participant.objects.filter(participant_conditions)
            }

        # === Этап 3: Поиск существующих участий ===
        existing_participations: dict[tuple[int, str, str, int], OlympiadParticipation] = {}
        all_participations = OlympiadParticipation.objects.filter(
            participant__in=list(existing_participants.values())
        ).select_related("subject")

        for ep in all_participations:
            part_key = (ep.participant_id, ep.subject.full_name.lower(), str(ep.stage), ep.year)
            existing_participations[part_key] = ep

        # === Этап 4: Создание/обновление участий ===
        to_create: list[OlympiadParticipation] = []
        to_update: list[OlympiadParticipation] = []

        for row in rows_data:
            participant = existing_participants.get(_row_key(row))
            if not participant:
                continue

            municipality = municipality_cache.get(row["municipality_name"])
            if not municipality:
                continue

            edu_key = (municipality.municipality_id, row["education_name"].lower())
            education = education_cache.get(edu_key)
            subject = subject_cache.get(row["subject_name"])

            if not education or not subject:
                continue

            lookup_key: tuple[int, str, str, int] = (
                participant.participant_id,
                row["subject_name"].lower(),
                str(row["stage"]),
                row["year"],
            )

            if lookup_key in existing_participations:
                ep = existing_participations[lookup_key]
                changed = False
                if ep.education_id != education.institution_id:
                    ep.education = education
                    changed = True
                if ep.class_field != row["class_field"]:
                    ep.class_field = row["class_field"]
                    changed = True
                if ep.status != row["status"]:
                    ep.status = row["status"]
                    changed = True
                if changed:
                    to_update.append(ep)
            else:
                to_create.append(
                    OlympiadParticipation(
                        participant=participant,
                        education=education,
                        subject=subject,
                        class_field=row["class_field"],
                        stage=row["stage"],
                        status=row["status"],
                        year=row["year"],
                    )
                )

        # === Этап 5: Запись в БД ===
        if to_create:
            OlympiadParticipation.objects.bulk_create(to_create, ignore_conflicts=True)
        if to_update:
            OlympiadParticipation.objects.bulk_update(
                to_update, ["education", "class_field", "status"]
            )

        return len(to_create), len(to_update)

    @action(detail=False, methods=["get"], url_path="filters")
    def get_filters(self, request: Request) -> Response:
        """Получить значения для фильтров участий в олимпиаде"""
        cached = VSOSHCacheService.get_filters()
        if cached:
            return Response(cached)

        stages = list(Limits.STAGE_VALUES)
        statuses = list(Limits.STATUS_VALUES)
        genders = list(Limits.GENDER_VALUES)
        classes = list(range(Limits.CLASS_MIN, Limits.CLASS_MAX + 1))[::-1]
        years = list(
            OlympiadParticipation.objects.values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )
        subjects = list(
            Subject.objects.values("subject_id", "full_name", "short_name")
            .distinct()
            .order_by("full_name")
        )
        educations = list(
            EducationInstitution.objects.values(
                "institution_id", "full_name", "short_name", "municipality"
            )
            .annotate(municipality_name=F("municipality__name"))
            .distinct()
            .order_by("full_name")
        )
        municipalities = list(
            Municipality.objects.values("municipality_id", "name").distinct().order_by("name")
        )
        data = {
            "stages": stages,
            "statuses": statuses,
            "genders": genders,
            "classes": classes,
            "years": years,
            "subjects": subjects,
            "educations": educations,
            "municipalities": municipalities,
        }
        VSOSHCacheService.set_filters(data)

        return Response(data)
