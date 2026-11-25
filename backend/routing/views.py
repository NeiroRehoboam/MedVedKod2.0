from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .models import RoutingResult
from .serializers import RoutingResultSerializer


# история маршрутизации
@extend_schema(tags=['Routing'])
class RoutingResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoutingResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            RoutingResult.objects
            .filter(session__patient__user=self.request.user)
            .select_related('session', 'specialty')
            .order_by('-created_at')
        )
