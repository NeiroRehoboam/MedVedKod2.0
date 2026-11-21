from rest_framework import viewsets
from .models import RoutingResult
from .serializers import RoutingResultSerializer

class RoutingResultViewSet(viewsets.ModelViewSet):
    queryset = RoutingResult.objects.all()
    serializer_class = RoutingResultSerializer