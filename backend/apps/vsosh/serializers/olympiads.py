import logging
from datetime import date, datetime
from typing import Any

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.common.serializers import FlexibleModelSerializer, get_field_error_messages

from ..constants import Errors, Limits, Messages
from ..models import OlympiadParticipation, Participant
from .common import _add_message

logger = logging.getLogger(__name__)


# =============================================================================
# Участия в олимпиаде - Create
# =============================================================================


class OlympiadParticipationCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания участия в олимпиаде"""

    message = serializers.CharField(read_only=True, required=False)
    participant_lastname = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150,
        error_messages=get_field_error_messages(Participant, "lastname"),
    )
    participant_firstname = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150,
        error_messages=get_field_error_messages(Participant, "firstname"),
    )
    participant_patronymic = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=150,
        error_messages=get_field_error_messages(Participant, "patronymic"),
    )
    participant_birth_date = serializers.DateField(
        write_only=True,
        required=False,
        allow_null=True,
        error_messages=get_field_error_messages(
            Participant,
            "birth_date",
            {
                "invalid": "Некорректная дата рождения участника",
            },
        ),
    )
    participant_gender = serializers.ChoiceField(
        choices=["М", "Ж"],
        write_only=True,
        required=False,
        default="М",
        error_messages=get_field_error_messages(
            Participant,
            "gender",
            {
                "invalid_choice": "Пол участника должен быть М или Ж",
            },
        ),
    )
    participant = serializers.PrimaryKeyRelatedField(
        queryset=Participant.objects.all(), required=False, allow_null=True, default=None
    )

    class Meta:
        model = OlympiadParticipation
        fields = (
            "olymp_id",
            "participant",
            "participant_lastname",
            "participant_firstname",
            "participant_patronymic",
            "participant_birth_date",
            "participant_gender",
            "education",
            "subject",
            "class_field",
            "stage",
            "status",
            "year",
            "message",
        )
        read_only_fields = ("olymp_id",)
        extra_kwargs: dict[str, Any] = {
            field: {"error_messages": get_field_error_messages(OlympiadParticipation, field)}
            for field in ("education", "subject", "class_field", "stage", "status", "year")
        }

    def validate_class_field(self, value: int) -> int:
        """Валидация класса"""
        if value < Limits.CLASS_MIN or value > Limits.CLASS_MAX:
            raise ValidationError(Errors.PARTICIPANT_CLASS_INVALID)
        return value

    def validate_year(self, value: int) -> int:
        """Валидация года"""
        current_year = datetime.now().year
        if value < Limits.YEAR_MIN or value > current_year + 1:
            raise ValidationError(Errors.PARTICIPATION_YEAR_INVALID)
        return value

    def validate_participant_birth_date(self, value: date) -> date:
        """Валидация диапазона даты рождения участника"""
        if value is None:
            return value
        if value < date(Limits.BIRTH_DATE_MIN_YEAR, 1, 1) or value > date.today():
            raise ValidationError(Errors.PARTICIPATION_DATE_INVALID)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Создание или поиск участника по данным"""
        # Проверка есть ли данные участника либо его id
        has_participant = attrs.get("participant") is not None

        has_participant_data = all(
            [
                attrs.get("participant_lastname"),
                attrs.get("participant_firstname"),
                attrs.get("participant_birth_date"),
            ]
        )

        if not has_participant and not has_participant_data:
            raise ValidationError({"participant": Errors.PARTICIPANT_NOT_SPECIFIED})

        if has_participant:
            for field in [
                "participant_lastname",
                "participant_firstname",
                "participant_patronymic",
                "participant_birth_date",
                "participant_gender",
            ]:
                attrs.pop(field, None)
        else:
            # Создаем участника из переданных данных
            participant_data = {}
            participant_fields = [
                "participant_lastname",
                "participant_firstname",
                "participant_patronymic",
                "participant_birth_date",
                "participant_gender",
            ]

            for field in participant_fields:
                value = attrs.pop(field, None)
                if value and not (field == "participant_patronymic" and value == ""):
                    participant_data[field] = value
                elif field == "participant_patronymic" and value == "":
                    pass

            # Создаем или получаем участника
            if participant_data:
                participant, _ = Participant.objects.get_or_create(
                    lastname=participant_data["participant_lastname"],
                    firstname=participant_data["participant_firstname"],
                    patronymic=participant_data.get("participant_patronymic", ""),
                    birth_date=participant_data["participant_birth_date"],
                    defaults={
                        "gender": participant_data.get("participant_gender", "М"),
                    },
                )
                attrs["participant"] = participant

        # Проверка unique_together: participant + subject + stage + year
        if (
            attrs.get("participant")
            and attrs.get("subject")
            and attrs.get("stage")
            and attrs.get("year")
        ):
            exists = OlympiadParticipation.objects.filter(
                participant=attrs["participant"],
                subject=attrs["subject"],
                stage=attrs["stage"],
                year=attrs["year"],
            ).exists()
            if exists:
                raise ValidationError(Errors.PARTICIPATION_EXIST)

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        _add_message(
            data,
            self.context.get("view"),
            Messages.PARTICIPATION_CREATED,
            Messages.PARTICIPATION_UPDATED,
        )
        return data


# =============================================================================
# Участия в олимпиаде - List/Retrieve
# =============================================================================


class OlympiadParticipationSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения участия в олимпиаде"""

    # Аннотированные поля
    participant_full_name = serializers.CharField(read_only=True)
    participant_lastname = serializers.CharField(read_only=True)
    participant_firstname = serializers.CharField(read_only=True)
    participant_patronymic = serializers.CharField(read_only=True)
    participant_birth_date = serializers.DateField(read_only=True)
    participant_gender = serializers.CharField(read_only=True)
    education_institution_name = serializers.CharField(read_only=True)
    education_short_name = serializers.CharField(read_only=True)
    municipality_name = serializers.CharField(read_only=True)
    municipality = serializers.SerializerMethodField(read_only=True)
    subject_full_name = serializers.CharField(read_only=True)
    subject_short_name = serializers.CharField(read_only=True)

    class Meta:
        model = OlympiadParticipation
        fields = (
            "olymp_id",
            "participant",
            "participant_full_name",
            "participant_lastname",
            "participant_firstname",
            "participant_patronymic",
            "participant_birth_date",
            "participant_gender",
            "education",
            "education_institution_name",
            "education_short_name",
            "municipality",
            "municipality_name",
            "subject",
            "subject_full_name",
            "subject_short_name",
            "class_field",
            "stage",
            "status",
            "year",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_municipality(self, obj) -> int | None:
        return obj.municipality if hasattr(obj, "municipality") else None


# =============================================================================
# Участия в олимпиаде - Update
# =============================================================================


class OlympiadParticipationUpdateSerializer(FlexibleModelSerializer):
    """Сериализатор для обновления участия в олимпиаде"""

    message = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = OlympiadParticipation
        fields = (
            "participant",
            "education",
            "subject",
            "class_field",
            "stage",
            "status",
            "year",
            "message",
        )
        extra_kwargs: dict[str, Any] = {
            field: {"error_messages": get_field_error_messages(OlympiadParticipation, field)}
            for field in (
                "participant",
                "education",
                "subject",
                "class_field",
                "stage",
                "status",
                "year",
            )
        }

    def validate_class_field(self, value: int) -> int:
        """Валидация класса"""
        if value < Limits.CLASS_MIN or value > Limits.CLASS_MAX:
            raise ValidationError(Errors.PARTICIPANT_CLASS_INVALID)
        return value

    def validate_year(self, value: int) -> int:
        """Валидация года"""
        current_year = datetime.now().year
        if value < Limits.YEAR_MIN or value > current_year + 1:
            raise ValidationError(Errors.PARTICIPATION_YEAR_INVALID)
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Проверка unique_together: participant + subject + stage + year"""
        assert self.instance is not None  # UpdateSerializer всегда имеет instance

        participant = attrs.get("participant", self.instance.participant)
        subject = attrs.get("subject", self.instance.subject)
        stage = attrs.get("stage", self.instance.stage)
        year = attrs.get("year", self.instance.year)

        if participant and subject and stage and year:
            exists = (
                OlympiadParticipation.objects.filter(
                    participant=participant,
                    subject=subject,
                    stage=stage,
                    year=year,
                )
                .exclude(pk=self.instance.pk)
                .exists()
            )
            if exists:
                raise ValidationError(Errors.PARTICIPATION_EXIST)

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        _add_message(
            data,
            self.context.get("view"),
            Messages.PARTICIPATION_CREATED,
            Messages.PARTICIPATION_UPDATED,
        )
        return data
