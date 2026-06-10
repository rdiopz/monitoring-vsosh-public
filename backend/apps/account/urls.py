from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ApplicationViewSet,
    AuditLogViewSet,
    LoginView,
    RefreshTokenView,
    RoleListView,
    SessionViewSet,
    SettingViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"session", SessionViewSet, basename="session")
router.register(r"application", ApplicationViewSet, basename="application")
router.register(r"user", UserViewSet, basename="user")
router.register(r"setting", SettingViewSet, basename="setting")
router.register(r"audit-log", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh-token"),
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("", include(router.urls)),
]
