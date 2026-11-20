from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Consultation, Message
from .serializers import SendMessageSerializer, MessageSerializer
from .services import process_user_message
from patients.models import Patient


class StartConsultationView(APIView):
    def post(self, request):
        patient_id = request.data.get('patient_id')
        if patient_id:
            patient = get_object_or_404(Patient, id=patient_id)
        else:
            patient = Patient.objects.first()
            if not patient:
                return Response({'error': 'Сначала создайте пациента'}, status=status.HTTP_400_BAD_REQUEST)

        consultation = Consultation.objects.create(patient=patient)
        welcome = Message.objects.create(
            consultation=consultation,
            role='assistant',
            content='Здравствуйте! Опишите, пожалуйста, вашу проблему или симптомы.'
        )

        return Response({
            'consultation_id': consultation.id,
            'status': consultation.status,
            'first_message': MessageSerializer(welcome).data,
        }, status=status.HTTP_201_CREATED)


class SendMessageView(APIView):
    def post(self, request, consultation_id):
        consultation = get_object_or_404(Consultation, id=consultation_id)

        if consultation.status != 'active':
            return Response({'error': 'Консультация уже завершена'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_text = serializer.validated_data['content']
        user_message = Message.objects.create(
            consultation=consultation, role='user', content=user_text,
        )

        history = [
            {'role': m.role, 'content': m.content}
            for m in consultation.messages.order_by('created_at')
        ]

        try:
            ai_response = process_user_message(consultation, user_text, history)
        except NotImplementedError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        ai_message = Message.objects.create(
            consultation=consultation,
            role='assistant',
            content=ai_response['reply'],
            is_emergency=ai_response['is_emergency'],
        )

        if ai_response['is_emergency']:
            consultation.status = 'emergency'
            consultation.emergency_reason = ai_response['emergency_reason']
            consultation.ai_summary = ai_response['reply']
            consultation.save()
        elif ai_response['is_final']:
            consultation.status = 'completed'
            consultation.ai_summary = ai_response['reply']
            consultation.save()

        return Response({
            'status': 'ok',
            'user_message': MessageSerializer(user_message).data,
            'ai_message': MessageSerializer(ai_message).data,
            'consultation_status': consultation.status,
            'is_emergency': ai_response['is_emergency'],
        }, status=status.HTTP_200_OK)