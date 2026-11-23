from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import *
from .serializers import *


@extend_schema(tags=['Dictionaries'])
class AllergyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllergyType.objects.filter(active=True)
    serializer_class = AllergyTypeSerializer


@extend_schema(tags=['Dictionaries'])
class HereditaryDiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HereditaryDisease.objects.filter(active=True)
    serializer_class = HereditaryDiseaseSerializer


@extend_schema(tags=['Dictionaries'])
class SpecialtyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialty.objects.filter(active=True)
    serializer_class = SpecialtySerializer


@extend_schema(tags=['Dictionaries'])
class AllergyReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllergyReference.objects.filter(active=True)
    serializer_class = AllergyReferenceSerializer


@extend_schema(tags=['Dictionaries'])
class MedicationReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MedicationReference.objects.filter(active=True)
    serializer_class = MedicationReferenceSerializer


@extend_schema(tags=['Dictionaries'])
class ComplaintCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ComplaintCategory.objects.filter(active=True)
    serializer_class = ComplaintCategorySerializer


@extend_schema(tags=["Dictionaries"])
class ChronicDiseaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChronicDisease.objects.all().order_by("name")
    serializer_class = ChronicDiseaseSerializer


@extend_schema(tags=["Dictionaries"])
class PaymentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentType.objects.filter(active=True).order_by("id")
    serializer_class = PaymentTypeSerializer
