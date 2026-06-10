from rest_framework import permissions

from .constants import Roles


class IsAdministrator(permissions.BasePermission):
    """
    Разрешение только для администраторов.
    Проверяет роль через request.user.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "role")
            and request.user.role
            and request.user.role.name == Roles.ADMINISTRATOR
        )
