from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import Anamnesis
from .serializers import FullAnamnesisSerializer

@extend_schema(tags=['Anamnesis'])
class AnamnesisViewSet(viewsets.ModelViewSet):
    serializer_class = FullAnamnesisSerializer
    def get_queryset(self):
        return Anamnesis.objects.filter(patient__user=self.request.user)