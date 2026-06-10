from django_filters import rest_framework as filters

from .models import (
    EducationInstitution,
    OlympiadParticipation,
    Participant,
)


class EducationInstitutionFilter(filters.FilterSet):
    """Фильтры для образовательных учреждений"""

    class Meta:
        model = EducationInstitution
        fields = {
            "municipality": ["exact", "in"],
        }


class ParticipantFilter(filters.FilterSet):
    """Фильтры для участников"""

    birth_date_after = filters.DateFilter(
        field_name="birth_date",
        lookup_expr="gte",
    )
    birth_date_before = filters.DateFilter(
        field_name="birth_date",
        lookup_expr="lte",
    )

    class Meta:
        model = Participant
        fields = {
            "gender": ["exact", "in"],
        }


class OlympiadParticipationFilter(filters.FilterSet):
    """Фильтры для участий в олимпиаде"""

    municipality__in = filters.BaseInFilter(field_name="education__municipality", lookup_expr="in")

    gender__in = filters.BaseInFilter(field_name="participant__gender", lookup_expr="in")

    municipality = filters.CharFilter(field_name="education__municipality", lookup_expr="exact")
    gender = filters.CharFilter(field_name="participant__gender", lookup_expr="exact")

    class Meta:
        model = OlympiadParticipation
        fields = {
            "participant": ["exact", "in"],
            "education": ["exact", "in"],
            "subject": ["exact", "in"],
            "stage": ["exact", "in"],
            "status": ["exact", "in"],
            "year": ["exact", "in"],
            "class_field": ["exact", "in"],
        }
