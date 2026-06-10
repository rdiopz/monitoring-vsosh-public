from django.core import checks
from django.db import connection, models


class PostgreSQLEnumField(models.CharField):
    """Кастомное поле для работы с PostgreSQL ENUM TYPE."""

    def __init__(self, *args, **kwargs):
        self.enum_type = kwargs.pop("enum_type", None)
        self.enum_values = kwargs.pop("enum_values", None)
        self.auto_create = kwargs.pop("auto_create", True)
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        """Возвращает тип поля для БД."""
        if connection.vendor == "postgresql" and self.enum_type:
            if self.auto_create and self.enum_values:
                self._ensure_enum_type(connection)
            return self.enum_type

        return super().db_type(connection)

    def _ensure_enum_type(self, connection):
        """Создаёт PostgreSQL ENUM TYPE, если он ещё не существует."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_type WHERE typname = %s",
                [self.enum_type],
            )

            if cursor.fetchone():
                return

            # Значения enum задаются из кода, поэтому здесь этого достаточно.
            values = ", ".join(f"'{value}'" for value in self.enum_values)
            cursor.execute(f"CREATE TYPE {self.enum_type} AS ENUM ({values})")

    def deconstruct(self):
        """Корректно сохраняет параметры поля в миграции."""
        name, path, args, kwargs = super().deconstruct()

        if self.enum_type:
            kwargs["enum_type"] = self.enum_type

        if self.enum_values:
            kwargs["enum_values"] = self.enum_values

        if not self.auto_create:
            kwargs["auto_create"] = self.auto_create

        return name, path, args, kwargs

    def check(self, **kwargs):
        """Валидация параметров поля."""
        errors = super().check(**kwargs)

        if connection.vendor == "postgresql":
            if not self.enum_type:
                errors.append(
                    checks.Warning(
                        "PostgreSQLEnumField без enum_type будет работать как CharField",
                        obj=self,
                        id="fields.W001",
                    )
                )

            if self.enum_values is not None and not self.enum_values:
                errors.append(
                    checks.Error(
                        "enum_values не может быть пустым списком",
                        obj=self,
                        id="fields.E001",
                    )
                )

        return errors
