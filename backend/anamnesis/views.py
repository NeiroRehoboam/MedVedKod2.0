from rest_framework import viewsets
from .models import Anamnesis
from .serializers import FullAnamnesisSerializer

class AnamnesisViewSet(viewsets.ModelViewSet):
    serializer_class = FullAnamnesisSerializer

    def get_queryset(self):
        return Anamnesis.objects.filter(patient__user=self.request.user)