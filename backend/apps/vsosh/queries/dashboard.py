from typing import Any

from django.db.models import (
    Case,
    Count,
    IntegerField,
    Q,
    QuerySet,
    Value,
    When,
)

from apps.vsosh.models import OlympiadParticipation, Participant

# =============================================================================
# Константы
# =============================================================================

STAGE_ORDER_CASE = Case(
    When(stage="ШЭ", then=Value(1)),
    When(stage="МЭ", then=Value(2)),
    When(stage="РЭ", then=Value(3)),
    When(stage="ЗЭ", then=Value(4)),
    default=Value(99),
    output_field=IntegerField(),
)

WINNER_FILTER = Q(status="победитель")
PRIZE_FILTER = Q(status="призёр")


# =============================================================================
# Вспомогательные функции
# =============================================================================


def _apply_subject_group_filter(
    queryset: QuerySet,
    subject_group: list[str] | None = None,
) -> QuerySet:
    """
    Фильтр по группе предметов.
    Для удобного разделения в дашборде.
    """
    selected = set(subject_group or [])

    if not selected or selected == {"vsosh", "olympiad"}:
        return queryset

    if selected == {"olympiad"}:
        return queryset.filter(subject__full_name__istartswith="Олимпиада")

    if selected == {"vsosh"}:
        return queryset.exclude(subject__full_name__istartswith="Олимпиада")

    return queryset


def _base_participations_queryset() -> QuerySet:
    """Получить queryset участий с подгрузкой связей"""
    return OlympiadParticipation.objects.select_related(
        "participant",
        "education",
        "education__municipality",
        "subject",
    )


def _full_name_from_participant(participant: Participant) -> str:
    """Сформировать ФИО"""
    return " ".join(
        part
        for part in [
            participant.lastname,
            participant.firstname,
            participant.patronymic,
        ]
        if part
    ).strip()


# =============================================================================
# Общий дашборд: фильтрация
# =============================================================================


def get_dashboard_filtered_queryset(filters: dict[str, Any]) -> QuerySet:
    """Сформировать queryset общего дашборда с применёнными фильтрами"""
    queryset = _base_participations_queryset()

    filter_map = {
        "year": "year__in",
        "stage": "stage__in",
        "subject_id": "subject_id__in",
        "municipality_id": "education__municipality_id__in",
        "education_id": "education_id__in",
        "class_field": "class_field__in",
        "status": "status__in",
        "gender": "participant__gender__in",
    }

    for param_key, lookup in filter_map.items():
        values = filters.get(param_key, [])
        if values:
            queryset = queryset.filter(**{lookup: values})

    queryset = _apply_subject_group_filter(queryset, filters.get("subject_group", []))

    return queryset


# =============================================================================
# Общий дашборд: агрегации
# =============================================================================


def get_dashboard_summary(queryset: QuerySet) -> dict[str, Any]:
    """Основные показатели дашборда"""
    data = queryset.aggregate(
        total_participations=Count("olymp_id"),
        total_participants=Count("participant_id", distinct=True),
        total_winners=Count("olymp_id", filter=WINNER_FILTER),
        total_prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        total_subjects=Count("subject_id", distinct=True),
        total_educations=Count("education_id", distinct=True),
        total_municipalities=Count("education__municipality_id", distinct=True),
    )

    return {key: value or 0 for key, value in data.items()}


def get_dashboard_by_stage(queryset: QuerySet) -> list[dict[str, Any]]:
    """Статистика по этапам"""
    return list(
        queryset.values("stage")
        .annotate(
            stage_order=STAGE_ORDER_CASE,
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("stage_order")
    )


def get_dashboard_by_year(queryset: QuerySet) -> list[dict[str, Any]]:
    """Статистика по годам"""
    return list(
        queryset.values("year")
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("year")
    )


def get_dashboard_by_subject(queryset: QuerySet, limit: int = 20) -> list[dict[str, Any]]:
    """Топ предметов"""
    return list(
        queryset.values(
            "subject_id",
            "subject__full_name",
            "subject__short_name",
        )
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("-participations", "subject__full_name")[:limit]
    )


def get_dashboard_by_municipality(
    queryset: QuerySet,
) -> list[dict[str, Any]]:
    """Статистика по муниципалитетам"""
    return list(
        queryset.values(
            "education__municipality_id",
            "education__municipality__name",
        )
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
            educations=Count("education_id", distinct=True),
        )
        .order_by("-participations", "education__municipality__name")
    )


def get_dashboard_by_education(queryset: QuerySet, limit: int = 20) -> list[dict[str, Any]]:
    """Топ учреждений"""
    return list(
        queryset.values(
            "education_id",
            "education__short_name",
            "education__full_name",
            "education__municipality__name",
        )
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("-participations", "education__short_name")[:limit]
    )


def get_dashboard_by_class(queryset: QuerySet) -> list[dict[str, Any]]:
    """Статистика по классам"""
    return list(
        queryset.values("class_field")
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
        )
        .order_by("class_field")
    )


def get_dashboard_by_status(queryset: QuerySet) -> list[dict[str, Any]]:
    """Статистика по статусам"""
    return list(queryset.values("status").annotate(count=Count("olymp_id")).order_by("-count"))


def get_dashboard_by_gender(queryset: QuerySet) -> list[dict[str, Any]]:
    """Статистика по полу"""
    return list(
        queryset.values("participant__gender")
        .annotate(
            participants=Count("participant_id", distinct=True),
            participations=Count("olymp_id"),
        )
        .order_by("participant__gender")
    )


def get_dashboard_stage_year_matrix(
    queryset: QuerySet,
) -> list[dict[str, Any]]:
    """Матрица: этапы по годам"""
    return list(
        queryset.values("year", "stage")
        .annotate(
            stage_order=STAGE_ORDER_CASE,
            participations=Count("olymp_id"),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("year", "stage_order")
    )


def build_dashboard_payload(filters: dict[str, Any]) -> dict[str, Any]:
    """Собрать полный набор запросов для общего дашборда"""
    queryset = get_dashboard_filtered_queryset(filters)

    return {
        "summary": get_dashboard_summary(queryset),
        "by_stage": get_dashboard_by_stage(queryset),
        "by_year": get_dashboard_by_year(queryset),
        "by_subject": get_dashboard_by_subject(queryset),
        "by_municipality": get_dashboard_by_municipality(queryset),
        "by_education": get_dashboard_by_education(queryset),
        "by_class": get_dashboard_by_class(queryset),
        "by_status": get_dashboard_by_status(queryset),
        "by_gender": get_dashboard_by_gender(queryset),
        "stage_year_matrix": get_dashboard_stage_year_matrix(queryset),
    }


# =============================================================================
# Дашборд конкретного участника: фильтрация
# =============================================================================


def get_participant_dashboard_queryset(
    participant_id: int,
    filters: dict[str, Any],
) -> QuerySet:
    """Сформировать queryset участий конкретного участника с фильтрами"""
    queryset = _base_participations_queryset().filter(participant_id=participant_id)

    filter_map = {
        "year": "year__in",
        "stage": "stage__in",
        "subject_id": "subject_id__in",
        "class_field": "class_field__in",
        "status": "status__in",
    }

    for param_key, lookup in filter_map.items():
        values = filters.get(param_key, [])
        if values:
            queryset = queryset.filter(**{lookup: values})

    return queryset


# =============================================================================
# Дашборд конкретного участника: агрегации
# =============================================================================


def get_participant_summary(queryset: QuerySet) -> dict[str, Any]:
    """Сводка по участнику"""
    data = queryset.aggregate(
        total_participations=Count("olymp_id"),
        total_subjects=Count("subject_id", distinct=True),
        total_years=Count("year", distinct=True),
        total_winners=Count("olymp_id", filter=WINNER_FILTER),
        total_prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
    )

    return {key: value or 0 for key, value in data.items()}


def get_participant_by_year(queryset: QuerySet) -> list[dict[str, Any]]:
    """Участия по годам"""
    return list(
        queryset.values("year")
        .annotate(
            participations=Count("olymp_id"),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("year")
    )


def get_participant_by_stage(queryset: QuerySet) -> list[dict[str, Any]]:
    """Участия по этапам"""
    return list(
        queryset.values("stage")
        .annotate(
            stage_order=STAGE_ORDER_CASE,
            participations=Count("olymp_id"),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("stage_order")
    )


def get_participant_by_subject(queryset: QuerySet) -> list[dict[str, Any]]:
    """Участия по предметам"""
    return list(
        queryset.values(
            "subject_id",
            "subject__full_name",
            "subject__short_name",
        )
        .annotate(
            participations=Count("olymp_id"),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("-participations", "subject__full_name")
    )


def get_participant_by_status(queryset: QuerySet) -> list[dict[str, Any]]:
    """Участия по статусам"""
    return list(queryset.values("status").annotate(count=Count("olymp_id")).order_by("-count"))


def get_participant_participations_table(
    queryset: QuerySet,
) -> list[dict[str, Any]]:
    """Таблица всех участий — без пагинации"""
    return list(
        queryset.values(
            "olymp_id",
            "year",
            "stage",
            "status",
            "class_field",
            "subject_id",
            "subject__full_name",
            "subject__short_name",
            "education_id",
            "education__full_name",
            "education__short_name",
            "education__municipality__name",
            "created_at",
            "updated_at",
        ).order_by("-year", "stage", "subject__full_name")
    )


def build_participant_dashboard_payload(
    participant: "Participant",
    filters: dict[str, Any],
) -> dict[str, Any]:
    """Собрать полный набор запросов дашборда по участнику"""
    queryset = get_participant_dashboard_queryset(participant.participant_id, filters)

    return {
        "participant": {
            "participant_id": participant.participant_id,
            "lastname": participant.lastname,
            "firstname": participant.firstname,
            "patronymic": participant.patronymic,
            "full_name": _full_name_from_participant(participant),
            "birth_date": participant.birth_date,
            "gender": participant.gender,
        },
        "summary": get_participant_summary(queryset),
        "by_year": get_participant_by_year(queryset),
        "by_stage": get_participant_by_stage(queryset),
        "by_subject": get_participant_by_subject(queryset),
        "by_status": get_participant_by_status(queryset),
        "participations": get_participant_participations_table(queryset),
    }
