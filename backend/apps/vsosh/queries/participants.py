import re
from datetime import date, datetime
from typing import Any

from django.db.models import CharField, F, Q, QuerySet

from apps.common.utils import ConcatWS
from apps.vsosh.models import Participant


def extract_name_and_birth_date(raw_query: str) -> tuple[str, date | None]:
    """
    Из строки извлекает часть фио и ищет дату по регулярному выражению
    """
    query = (raw_query or "").strip()
    if not query:
        return "", None

    patterns = [
        (r"\b\d{2}\.\d{2}\.\d{4}\b", "%d.%m.%Y"),
        (r"\b\d{4}-\d{2}-\d{2}\b", "%Y-%m-%d"),
    ]

    for pattern, fmt in patterns:
        match = re.search(pattern, query)
        if not match:
            continue

        try:
            birth_date = datetime.strptime(match.group(0), fmt).date()
        except ValueError:
            continue

        name_query = re.sub(pattern, " ", query)
        name_query = re.sub(r"\s+", " ", name_query).strip()
        return name_query, birth_date

    query = re.sub(r"\s+", " ", query).strip()
    return query, None


def _apply_search_filters(
    queryset: QuerySet,
    name_query: str,
    birth_date: date | None,
) -> QuerySet:
    """Применить фильтры поиска по ФИО и дате рождения к queryset"""
    if birth_date:
        queryset = queryset.filter(birth_date=birth_date)

    if name_query:
        parts = [part.strip() for part in name_query.split(" ") if part.strip()]

        for part in parts:
            queryset = queryset.filter(
                Q(lastname__icontains=part)
                | Q(firstname__icontains=part)
                | Q(patronymic__icontains=part)
            )

        queryset = queryset.order_by("lastname", "firstname", "patronymic", "birth_date")
    else:
        queryset = queryset.order_by("-participant_id")

    return queryset


PARTICIPANT_SEARCH_FIELDS = (
    "participant_id",
    "lastname",
    "firstname",
    "patronymic",
    "birth_date",
    "gender",
    "full_name",
)


def _get_base_queryset() -> QuerySet:
    """Получить queryset с ФИО"""
    return Participant.objects.annotate(
        full_name=ConcatWS(
            " ",
            F("lastname"),
            F("firstname"),
            F("patronymic"),
            output_field=CharField(),
        )
    )


def search_participants(
    q: str = "",
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """
    Поиск участников с возможностью бесконечного скролла
    """
    name_query, birth_date = extract_name_and_birth_date(q)

    queryset = _get_base_queryset()
    queryset = _apply_search_filters(queryset, name_query, birth_date)

    total_count = queryset.count()

    results = list(queryset.values(*PARTICIPANT_SEARCH_FIELDS)[offset : offset + limit])

    next_offset = offset + limit
    has_more = next_offset < total_count

    return {
        "count": total_count,
        "limit": limit,
        "offset": offset,
        "next_offset": next_offset if has_more else None,
        "has_more": has_more,
        "results": results,
    }
