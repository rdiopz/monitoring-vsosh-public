from typing import Any

from django.db.models import (
    Case,
    CharField,
    Count,
    F,
    IntegerField,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)

from apps.common.utils import ConcatWS

# =============================================================================
# Константы
# =============================================================================

WINNER_FILTER = Q(status="победитель")
PRIZE_FILTER = Q(status="призёр")
PARTICIPANT_FILTER = Q(status="участник")

# Весовые коэффициенты для рейтинга
RATING_CASE = Case(
    When(status="победитель", then=Value(5)),
    When(status="призёр", then=Value(3)),
    When(status="участник", then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)


# =============================================================================
# Отчёты: агрегации и сводки
# =============================================================================


def report_stage_year(queryset: QuerySet) -> list[dict[str, Any]]:
    """
    Сводка по этапам и годам.
    Строки: год + этап.
    """
    return list(
        queryset.values("year", "stage")
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("year", "stage")
    )


def report_municipality(queryset: QuerySet) -> list[dict[str, Any]]:
    """
    Статистика по муниципалитетам.
    Одна строка — один муниципалитет.
    """
    return list(
        queryset.values(municipality_name=F("education__municipality__name"))
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
            educations=Count("education_id", distinct=True),
        )
        .order_by("-participations")
    )


def report_subject(queryset: QuerySet) -> list[dict[str, Any]]:
    """
    Статистика по предметам.
    Одна строка — один предмет.
    """
    return list(
        queryset.values(subject_name=F("subject__full_name"))
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("-participations")
    )


def report_education(queryset: QuerySet) -> list[dict[str, Any]]:
    """
    Детализация по учреждениям.
    Одна строка — одно учреждение.
    """
    return list(
        queryset.values(
            municipality_name=F("education__municipality__name"),
            education_name=F("education__full_name"),
        )
        .annotate(
            participations=Count("olymp_id"),
            participants=Count("participant_id", distinct=True),
            winners=Count("olymp_id", filter=WINNER_FILTER),
            prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
        )
        .order_by("municipality_name", "-participations")
    )


def report_winners(queryset: QuerySet) -> list[dict[str, Any]]:
    """
    Список победителей и призёров.
    Каждая строка — одно участие конкретного человека.
    """
    return list(
        queryset.filter(status__in=["победитель", "призёр"])
        .annotate(
            full_name=ConcatWS(
                " ",
                F("participant__lastname"),
                F("participant__firstname"),
                F("participant__patronymic"),
                output_field=CharField(),
            ),
        )
        .values(
            "full_name",
            "participant__birth_date",
            "participant__gender",
            "subject__full_name",
            "education__full_name",
            "education__municipality__name",
            "class_field",
            "stage",
            "status",
            "year",
        )
        .order_by("-year", "stage", "status", "full_name")
    )


def report_rating(queryset: QuerySet) -> list[dict[str, Any]]:
    """
    Рейтинг обучающихся.
    Баллы: победитель=5, призёр=3, участник=1.
    Одна строка — один участник.
    Сортировка по убыванию суммарного балла.
    """
    return list(
        queryset.values(
            "participant_id",
            participant_lastname=F("participant__lastname"),
            participant_firstname=F("participant__firstname"),
            participant_patronymic=F("participant__patronymic"),
            participant_birth_date=F("participant__birth_date"),
            participant_gender=F("participant__gender"),
            municipality_name=F("education__municipality__name"),
            education_name=F("education__full_name"),
        )
        .annotate(
            full_name=ConcatWS(
                " ",
                F("participant__lastname"),
                F("participant__firstname"),
                F("participant__patronymic"),
                output_field=CharField(),
            ),
            total_participations=Count("olymp_id"),
            total_winners=Count("olymp_id", filter=WINNER_FILTER),
            total_prize_winners=Count("olymp_id", filter=PRIZE_FILTER),
            total_participants=Count("olymp_id", filter=PARTICIPANT_FILTER),
            rating=Sum(RATING_CASE),
        )
        .order_by("-rating", "-total_winners", "-total_prize_winners", "full_name")
    )
