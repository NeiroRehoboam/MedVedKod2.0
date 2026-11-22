from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import RoutingResult
from .serializers import RoutingResultSerializer

@extend_schema(tags=['Routing'])
class RoutingResultViewSet(viewsets.ModelViewSet):
    queryset = RoutingResult.objects.all()
    serializer_class = RoutingResultSerializer