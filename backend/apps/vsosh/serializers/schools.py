import logging
from typing import Any

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.common.serializers import FlexibleModelSerializer, get_field_error_messages

from ..constants import Errors, Messages
from ..models import EducationInstitution
from .common import _add_message

logger = logging.getLogger(__name__)


# =============================================================================
# Образовательное учреждение
# =============================================================================


class EducationInstitutionSerializer(FlexibleModelSerializer):
    """Сериализатор для образовательных учреждений"""

    message = serializers.CharField(read_only=True, required=False)
    municipality_name = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = EducationInstitution
        fields = (
            "institution_id",
            "municipality",
            "municipality_name",
            "full_name",
            "short_name",
            "message",
        )
        read_only_fields = ("institution_id", "municipality_name")
        extra_kwargs: dict[str, Any] = {
            "municipality": {
                "error_messages": get_field_error_messages(EducationInstitution, "municipality"),
            },
            "full_name": {
                "error_messages": get_field_error_messages(EducationInstitution, "full_name"),
            },
            "short_name": {
                "error_messages": get_field_error_messages(EducationInstitution, "short_name"),
            },
        }

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Проверка уникальности в рамках муниципалитета без учёта регистра"""
        municipality = attrs.get("municipality")
        full_name = attrs.get("full_name")
        short_name = attrs.get("short_name")

        if not municipality:
            municipality = getattr(self.instance, "municipality", None)

        if municipality and full_name:
            queryset = EducationInstitution.objects.filter(
                municipality=municipality,
                full_name__iexact=full_name,
            )
            if self.instance:
                queryset = queryset.exclude(institution_id=self.instance.institution_id)

            if queryset.exists():
                raise ValidationError({"full_name": Errors.INSTITUTION_EXISTS})

        if municipality and short_name:
            queryset = EducationInstitution.objects.filter(
                municipality=municipality,
                short_name__iexact=short_name,
            )
            if self.instance:
                queryset = queryset.exclude(institution_id=self.instance.institution_id)

            if queryset.exists():
                raise ValidationError({"short_name": Errors.INSTITUTION_EXISTS})

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        _add_message(
            data,
            self.context.get("view"),
            Messages.INSTITUTION_CREATED,
            Messages.INSTITUTION_UPDATED,
        )
        return data
