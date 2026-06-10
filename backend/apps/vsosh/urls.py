from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DashboardParticipantView,
    DashboardView,
    EducationInstitutionViewSet,
    MunicipalityViewSet,
    OlympiadParticipationViewSet,
    ParticipantViewSet,
    ReportDownloadView,
    ReportsListView,
    SubjectViewSet,
)

router = DefaultRouter()
router.register(r"municipality", MunicipalityViewSet, basename="municipality")
router.register(r"subject", SubjectViewSet, basename="subject")
router.register(
    r"education-institution", EducationInstitutionViewSet, basename="education-institution"
)
router.register(r"participant", ParticipantViewSet, basename="participant")
router.register(
    r"olympiad-participation", OlympiadParticipationViewSet, basename="olympiad-participation"
)

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/", DashboardView.as_view(), name="vsosh-dashboard"),
    path(
        "dashboard/participants/<int:participant_id>/",
        DashboardParticipantView.as_view(),
        name="vsosh-dashboard-participant",
    ),
    path(
        "reports/",
        ReportsListView.as_view(),
        name="vsosh-reports-list",
    ),
    path(
        "reports/<str:report_key>/",
        ReportDownloadView.as_view(),
        name="vsosh-report-download",
    ),
]
