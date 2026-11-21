from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Patient
from .serializers import PatientSerializer
from anamnesis.models import Anamnesis
from routing.models import Routing
from ai_assis.models import Consultation, Message


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class FullRecordView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data

        patient_serializer = PatientSerializer(data=data.get('patient', {}))
        if not patient_serializer.is_valid():
            return Response(patient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        patient = patient_serializer.save()

        anamnesis_id = None
        if 'anamnesis' in data and data['anamnesis']:
            anamnesis = Anamnesis.objects.create(
                patient=patient,
                description=data['anamnesis']['description'],
            )
            anamnesis_id = anamnesis.id

        routing_id = None
        if 'routing' in data and data['routing']:
            routing = Routing.objects.create(
                patient=patient,
                destination=data['routing']['destination'],
            )
            routing_id = routing.id

        consultation_id = None
        if 'consultation' in data and data['consultation']:
            consultation = Consultation.objects.create(patient=patient)
            Message.objects.create(
                consultation=consultation,
                role='user',
                content=data['consultation']['initial_message'],
            )
            consultation_id = consultation.id

        return Response({
            'status': 'ok',
            'patient_id': patient.id,
            'anamnesis_id': anamnesis_id,
            'routing_id': routing_id,
            'consultation_id': consultation_id,
        }, status=status.HTTP_201_CREATED)