from rest_framework import serializers

from apps.vsosh.constants import Limits


class ReportFiltersSerializer(serializers.Serializer):
    """Фильтры для генерации отчётов"""

    year = serializers.ListField(
        child=serializers.IntegerField(min_value=Limits.YEAR_MIN),
        required=False,
        default=list,
    )

    stage = serializers.ListField(
        child=serializers.ChoiceField(choices=Limits.STAGE_VALUES),
        required=False,
        default=list,
    )

    status = serializers.ListField(
        child=serializers.ChoiceField(choices=Limits.STATUS_VALUES),
        required=False,
        default=list,
    )

    subject_id = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )

    municipality_id = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )

    education_id = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )
