from rest_framework import viewsets
from .models import Anamnesis
from .serializers import AnamnesisSerializer

class AnamnesisViewSet(viewsets.ModelViewSet):
    queryset = Anamnesis.objects.all()
    serializer_class = AnamnesisSerializer