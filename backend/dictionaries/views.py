from rest_framework import viewsets
from .models import (
    SmokingStatus, AlcoholStatus, AllergyType, MedicalEventType, 
    HereditaryDisease, Specialty, AllergyReference, MedicationReference,
    ComplaintCategory
)
from .serializers import (
    SmokingStatusSerializer, AlcoholStatusSerializer, AllergyTypeSerializer, 
    MedicalEventTypeSerializer, HereditaryDiseaseSerializer, SpecialtySerializer, 
    AllergyReferenceSerializer, MedicationReferenceSerializer,
    ComplaintCategorySerializer
)

class SmokingStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SmokingStatus.objects.filter(active=True)
    serializer_class = SmokingStatusSerializer

class AlcoholStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlcoholStatus.objects.filter(active=True)
    serializer_class = AlcoholStatusSerializer

class AllergyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllergyType.objects.filter(active=True)
    serializer_class = AllergyTypeSerializer

class MedicalEventTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MedicalEventType.objects.filter(active=True)
    serializer_class = MedicalEventTypeSerializer

class HereditaryDiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HereditaryDisease.objects.filter(active=True)
    serializer_class = HereditaryDiseaseSerializer

class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialty.objects.filter(active=True)
    serializer_class = SpecialtySerializer

class AllergyReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllergyReference.objects.filter(active=True)
    serializer_class = AllergyReferenceSerializer

class MedicationReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MedicationReference.objects.filter(active=True)
    serializer_class = MedicationReferenceSerializer

class ComplaintCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ComplaintCategory.objects.filter(active=True)
    serializer_class = ComplaintCategorySerializer