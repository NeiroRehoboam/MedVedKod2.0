from rest_framework import viewsets
from .models import Routing
from .serializers import RoutingSerializer

class RoutingViewSet(viewsets.ModelViewSet):
    queryset = Routing.objects.all()
    serializer_class = RoutingSerializer