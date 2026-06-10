import logging
from datetime import date
from typing import Any

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.common.serializers import FlexibleModelSerializer, get_field_error_messages

from ..constants import Errors, Limits, Messages
from ..models import Participant
from .common import _add_message

logger = logging.getLogger(__name__)


# =============================================================================
# Участник
# =============================================================================


class ParticipantSerializer(FlexibleModelSerializer):
    """Сериализатор для участников"""

    message = serializers.CharField(read_only=True, required=False)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Participant
        fields = (
            "participant_id",
            "lastname",
            "firstname",
            "patronymic",
            "birth_date",
            "gender",
            "full_name",
            "message",
        )
        read_only_fields = ("participant_id", "full_name")
        extra_kwargs: dict[str, Any] = {
            "lastname": {
                "error_messages": get_field_error_messages(Participant, "lastname"),
            },
            "firstname": {
                "error_messages": get_field_error_messages(Participant, "firstname"),
            },
            "patronymic": {
                "error_messages": get_field_error_messages(Participant, "patronymic"),
            },
            "birth_date": {
                "error_messages": get_field_error_messages(
                    Participant,
                    "birth_date",
                    {
                        "invalid": "Введите корректную дату рождения",
                    },
                ),
            },
            "gender": {
                "error_messages": get_field_error_messages(
                    Participant,
                    "gender",
                    {
                        "invalid_choice": "Пол должен быть М или Ж",
                    },
                ),
            },
        }

    def validate_birth_date(self, value: date) -> date:
        """Валидация диапазона даты рождения"""
        if value < date(Limits.BIRTH_DATE_MIN_YEAR, 1, 1) or value > date.today():
            raise ValidationError(Errors.PARTICIPANT_DATE_INVALID)

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        _add_message(
            data,
            self.context.get("view"),
            Messages.PARTICIPANT_CREATED,
            Messages.PARTICIPANT_UPDATED,
        )
        return data


class ParticipantSearchSerializer(serializers.Serializer):
    """Параметры запроса для поиска участников"""

    # Запрос (query)
    q = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=500,
    )

    # Сколько отображать данных + смещение
    limit = serializers.IntegerField(
        required=False,
        default=20,
        min_value=1,
        max_value=100,
    )

    offset = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
    )
