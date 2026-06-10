from rest_framework import serializers

from apps.vsosh.constants import Limits


class DashboardQuerySerializer(serializers.Serializer):
    """Параметры запроса для общего дашборда"""

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

    class_field = serializers.ListField(
        child=serializers.IntegerField(
            min_value=Limits.CLASS_MIN,
            max_value=Limits.CLASS_MAX,
        ),
        required=False,
        default=list,
    )

    status = serializers.ListField(
        child=serializers.ChoiceField(choices=Limits.STATUS_VALUES),
        required=False,
        default=list,
    )

    gender = serializers.ListField(
        child=serializers.ChoiceField(choices=Limits.GENDER_VALUES),
        required=False,
        default=list,
    )

    subject_group = serializers.ListField(
        child=serializers.ChoiceField(choices=["vsosh", "olympiad"]),
        required=False,
        default=list,
    )


class DashboardParticipantQuerySerializer(serializers.Serializer):
    """Параметры запроса для дашборда конкретного участника"""

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

    subject_id = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )

    class_field = serializers.ListField(
        child=serializers.IntegerField(
            min_value=Limits.CLASS_MIN,
            max_value=Limits.CLASS_MAX,
        ),
        required=False,
        default=list,
    )

    status = serializers.ListField(
        child=serializers.ChoiceField(choices=Limits.STATUS_VALUES),
        required=False,
        default=list,
    )
