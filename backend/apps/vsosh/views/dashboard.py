from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.vsosh.models import Participant
from apps.vsosh.queries import (
    build_dashboard_payload,
    build_participant_dashboard_payload,
)
from apps.vsosh.serializers.dashboard import (
    DashboardParticipantQuerySerializer,
    DashboardQuerySerializer,
)


class DashboardView(generics.GenericAPIView):
    """
    Общий дашборд ВсОШ.

    GET /vsosh/dashboard/
    GET /vsosh/dashboard/?year=2024&year=2025&stage=РЭ&gender=М
    """

    pagination_class = None
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardQuerySerializer

    def get(self, request: Request) -> Response:
        """Для получения полного набора данных для дашборда"""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = build_dashboard_payload(serializer.validated_data)
        return Response(data)


class DashboardParticipantView(generics.GenericAPIView):
    """
    Дашборд конкретного участника.

    GET /vsosh/dashboard/participants/<id>/
    GET /vsosh/dashboard/participants/<id>/?year=2024&stage=РЭ
    """

    pagination_class = None
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardParticipantQuerySerializer

    def get_participant(self, participant_id: int) -> Participant:
        """Получить участника или 404"""
        return get_object_or_404(
            Participant,
            participant_id=participant_id,
        )

    def get(self, request: Request, participant_id: int) -> Response:
        """Для получения полного набора данных для дашборда по участнику"""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        participant = self.get_participant(participant_id)

        data = build_participant_dashboard_payload(
            participant=participant,
            filters=serializer.validated_data,
        )
        return Response(data)
