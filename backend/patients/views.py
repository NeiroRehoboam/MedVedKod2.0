from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import Patient
from .serializers import PatientSerializer

# пациенты текущего пользователя
@extend_schema(tags=['Patients'])
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    def get_queryset(self): return Patient.objects.filter(user=self.request.user)