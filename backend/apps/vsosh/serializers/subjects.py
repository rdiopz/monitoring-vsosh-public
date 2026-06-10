import logging
from typing import Any

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.common.serializers import FlexibleModelSerializer, get_field_error_messages

from ..constants import Errors, Messages
from ..models import Subject
from .common import _add_message

logger = logging.getLogger(__name__)


# =============================================================================
# Предмет
# =============================================================================


class SubjectSerializer(FlexibleModelSerializer):
    """Сериализатор для предметов"""

    message = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Subject
        fields = ("subject_id", "full_name", "short_name", "message")
        read_only_fields = ("subject_id",)
        extra_kwargs: dict[str, Any] = {
            "full_name": {
                "validators": [],
                "error_messages": get_field_error_messages(Subject, "full_name"),
            },
            "short_name": {
                "validators": [],
                "error_messages": get_field_error_messages(Subject, "short_name"),
            },
        }

    def validate_full_name(self, value: str) -> str:
        """Проверка уникальности полного названия без учёта регистра"""
        queryset = Subject.objects.all()
        if self.instance:
            queryset = queryset.exclude(subject_id=self.instance.subject_id)

        if queryset.filter(full_name__iexact=value).exists():
            raise ValidationError(Errors.SUBJECT_EXISTS)

        return value

    def validate_short_name(self, value: str) -> str:
        """Проверка уникальности краткого названия без учёта регистра"""
        queryset = Subject.objects.all()
        if self.instance:
            queryset = queryset.exclude(subject_id=self.instance.subject_id)

        if queryset.filter(short_name__iexact=value).exists():
            raise ValidationError(Errors.SUBJECT_SHORT_EXISTS)

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        _add_message(
            data,
            self.context.get("view"),
            Messages.SUBJECT_CREATED,
            Messages.SUBJECT_UPDATED,
        )
        return data
