import logging
from typing import Any

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.common.serializers import FlexibleModelSerializer, get_field_error_messages

from ..constants import Errors, Messages
from ..models import Municipality
from .common import _add_message

logger = logging.getLogger(__name__)


# =============================================================================
# Муниципалитет
# =============================================================================


class MunicipalitySerializer(FlexibleModelSerializer):
    """Сериализатор для муниципалитетов"""

    message = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Municipality
        fields = ("municipality_id", "name", "message")
        read_only_fields = ("municipality_id",)
        extra_kwargs: dict[str, Any] = {
            "name": {
                "validators": [],
                "error_messages": get_field_error_messages(Municipality, "name"),
            }
        }

    def validate_name(self, value: str) -> str:
        """Проверка уникальности без учёта регистра"""
        queryset = Municipality.objects.all()
        if self.instance:
            queryset = queryset.exclude(municipality_id=self.instance.municipality_id)

        if queryset.filter(name__iexact=value).exists():
            raise ValidationError(Errors.MUNICIPALITY_EXISTS)

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        _add_message(
            data,
            self.context.get("view"),
            Messages.MUNICIPALITY_CREATED,
            Messages.MUNICIPALITY_UPDATED,
        )
        return data
