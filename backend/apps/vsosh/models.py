from datetime import date

from django.db import models
from django.db.models import CheckConstraint, Func, Q, UniqueConstraint
from django.db.models.functions import Lower

from apps.common.fields import PostgreSQLEnumField


class CurrentDate(Func):
    template = "CURRENT_DATE"
    output_field = models.DateField()


class CurrentYear(Func):
    template = "EXTRACT(YEAR from CURRENT_DATE)::INTEGER"
    output_field = models.IntegerField()


class Municipality(models.Model):
    municipality_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, verbose_name="Название")

    class Meta:
        db_table = "municipality"
        verbose_name = "муниципалитет"
        verbose_name_plural = "муниципалитеты"
        constraints = [
            UniqueConstraint(Lower("name"), name="unique_municipality_name_ci"),
        ]

    def __str__(self):
        return self.name


class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100, verbose_name="Полное название")
    short_name = models.CharField(max_length=25, verbose_name="Краткое название")

    class Meta:
        db_table = "subject"
        verbose_name = "предмет"
        verbose_name_plural = "предметы"
        constraints = [
            UniqueConstraint(Lower("full_name"), name="unique_subject_full_name_ci"),
            UniqueConstraint(Lower("short_name"), name="unique_subject_short_name_ci"),
        ]

    def __str__(self):
        return self.full_name


class EducationInstitution(models.Model):
    institution_id = models.AutoField(primary_key=True)
    municipality = models.ForeignKey(
        Municipality,
        models.DO_NOTHING,
        db_column="municipality_id",
        related_name="education_institutions",
        verbose_name="Муниципалитет",
    )
    full_name = models.CharField(max_length=500, verbose_name="Полное наименование")
    short_name = models.CharField(max_length=300, verbose_name="Краткое наименование")

    class Meta:
        db_table = "education_institution"
        indexes = [
            models.Index(fields=["municipality"]),
        ]
        verbose_name = "образовательное учреждение"
        verbose_name_plural = "образовательные учреждения"
        constraints = [
            UniqueConstraint(Lower("full_name"), "municipality", name="unique_edu_full_name_ci"),
            UniqueConstraint(Lower("short_name"), "municipality", name="unique_edu_short_name_ci"),
        ]

    def __str__(self):
        return self.full_name


class Participant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    lastname = models.CharField(max_length=150, verbose_name="Фамилия")
    firstname = models.CharField(max_length=150, verbose_name="Имя")
    patronymic = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Отчество",
    )
    birth_date = models.DateField(verbose_name="Дата рождения")
    gender = PostgreSQLEnumField(
        enum_type="gender_type", enum_values=["М", "Ж"], default="М", verbose_name="Пол"
    )

    class Meta:
        db_table = "participant"
        indexes = [
            models.Index(fields=["lastname", "firstname", "patronymic"]),
        ]
        constraints = [
            CheckConstraint(
                condition=Q(birth_date__gte=date(1950, 1, 1)) & Q(birth_date__lte=CurrentDate()),
                name="birth_date_check",
                violation_error_code="Некорректная дата рождения. Укажите дату с 1950 года по текущую.",
            )
        ]
        verbose_name = "участник"
        verbose_name_plural = "участники"

    def get_full_name(self):
        """Полное ФИО участника"""
        parts = [self.lastname, self.firstname]
        if self.patronymic:
            parts.append(self.patronymic)
        return " ".join(parts)

    def __str__(self):
        return f"{self.get_full_name()} — {self.birth_date} — {self.gender}"


class OlympiadParticipation(models.Model):
    olymp_id = models.AutoField(primary_key=True)
    participant = models.ForeignKey(
        Participant,
        models.CASCADE,
        db_column="participant_id",
        related_name="olympiad_participations",
        verbose_name="Участник",
    )
    education = models.ForeignKey(
        EducationInstitution,
        models.DO_NOTHING,
        db_column="education_id",
        related_name="olympiad_participations",
        verbose_name="Образовательное учреждение",
    )
    subject = models.ForeignKey(
        Subject,
        models.DO_NOTHING,
        db_column="subject_id",
        related_name="olympiad_participations",
        verbose_name="Предмет",
    )
    class_field = models.SmallIntegerField(
        db_column="class",
        verbose_name="Класс",
    )
    stage = PostgreSQLEnumField(
        enum_type="stage_type",
        enum_values=["ШЭ", "МЭ", "РЭ", "ЗЭ"],
        verbose_name="Этап",
    )
    status = PostgreSQLEnumField(
        enum_type="participation_status_type",
        enum_values=["победитель", "призёр", "участник"],
        verbose_name="Статус",
    )
    year = models.SmallIntegerField(verbose_name="Год")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "olympiad_participation"
        unique_together = (("participant", "subject", "stage", "year"),)
        indexes = [
            models.Index(fields=["participant"]),
            models.Index(fields=["stage", "status"]),
            models.Index(fields=["subject"]),
            models.Index(fields=["education"]),
            models.Index(fields=["year"]),
        ]
        constraints = [
            CheckConstraint(
                condition=Q(class_field__range=(1, 11)),
                name="class_check",
                violation_error_message="Некорректный класс. Допустимые значения: от 1 до 11.",
            ),
            CheckConstraint(
                condition=Q(year__gte=1960) & Q(year__lte=CurrentYear() + 1),
                name="year_check",
                violation_error_message="Некорректный год олимпиады. Допустимый диапазон: с 1960 года по следующий за текущим.",
            ),
        ]
        verbose_name = "участие в олимпиаде"
        verbose_name_plural = "участия в олимпиадах"

    def __str__(self):
        return f"{self.participant.get_full_name()} — {self.stage} ({self.year})"
