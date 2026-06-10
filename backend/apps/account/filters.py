from django_filters import rest_framework as filters

from .models import Application, AuditLog, UserAccount


class ApplicationFilter(filters.FilterSet):
    """Фильтры для заявок"""

    created_after = filters.DateTimeFilter(
        field_name="application_datetime",
        lookup_expr="gte",
    )
    created_before = filters.DateTimeFilter(
        field_name="application_datetime",
        lookup_expr="lte",
    )

    class Meta:
        model = Application
        fields = {"status": ["exact", "in"], "reviewed_by": ["exact", "in", "isnull"]}


class UserFilter(filters.FilterSet):
    """Фильтры для пользователей"""

    created_after = filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_before = filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )
    last_login_after = filters.DateTimeFilter(
        field_name="last_login",
        lookup_expr="gte",
    )
    last_login_before = filters.DateTimeFilter(
        field_name="last_login",
        lookup_expr="lte",
    )

    class Meta:
        model = UserAccount
        fields = {
            "is_active": ["exact"],
            "role": ["exact", "in"],
        }


class AuditLogFilter(filters.FilterSet):
    """Фильтры для логов аудита"""

    timestamp_from = filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    timestamp_to = filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = AuditLog
        fields = {
            "action": ["exact", "in"],
            "model_name": ["exact", "in"],
            "object_id": ["exact"],
            "ip_address": ["exact"],
        }
