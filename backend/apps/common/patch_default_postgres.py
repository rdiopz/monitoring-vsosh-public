"""
Патч для DEFAULT в PostgreSQL.
"""

import sys

import django.db.models.fields as fields

_origins = {
    "dt": fields.DateTimeField.db_type,
    "bool": fields.BooleanField.db_type,
}


def _wrap(original):
    """Создает обертку для db_type"""

    def wrapper(self, *args, **kwargs):
        sql = original(self, *args, **kwargs)

        conn = args[0] if args else kwargs.get("connection")

        if conn and conn.vendor == "postgresql":
            # Временное поле
            if original == _origins["dt"] and (
                getattr(self, "auto_now_add", False) or getattr(self, "auto_now", False)
            ):
                return f"{sql} DEFAULT CURRENT_TIMESTAMP"

            # Булевое поле
            if original == _origins["bool"] and hasattr(self, "default"):
                if self.default is True:
                    return f"{sql} DEFAULT true"
                if self.default is False:
                    return f"{sql} DEFAULT false"

        return sql

    return wrapper


# Применяем патчи
fields.DateTimeField.db_type = _wrap(_origins["dt"])  # type: ignore[method-assign]
fields.BooleanField.db_type = _wrap(_origins["bool"])  # type: ignore[method-assign]

print("PostgreSQL DEFAULT патч применен", file=sys.stderr)
