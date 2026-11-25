from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Patient
from .serializers import PatientSerializer, PreferredPaymentUpdateSerializer


# пациенты текущего пользователя
@extend_schema(tags=['Patients'])
class PatientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(user=self.request.user)


# приоритетная оплата сохраняется отдельно, чтобы не открывать запись остальных полей
@extend_schema(tags=['Patients'])
class PreferredPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PreferredPaymentUpdateSerializer,
        responses={200: PatientSerializer},
    )
    def patch(self, request):
        patient = get_object_or_404(Patient, user=request.user)
        serializer = PreferredPaymentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient.preferred_payment = serializer.validated_data['preferred_payment']
        patient.save(update_fields=['preferred_payment'])
        return Response(PatientSerializer(patient).data)
