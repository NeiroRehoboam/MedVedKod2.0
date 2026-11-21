from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Session, SessionQuestion
from .serializers import SendMessageSerializer, SessionSerializer
from .services import process_user_message

class StartSessionView(APIView):
    def post(self, request):
        try:
            patient = request.user.patient
        except Exception:
            return Response({'error': 'Нет карты пациента'}, status=status.HTTP_400_BAD_REQUEST)

        session = Session.objects.create(patient=patient)
        SessionQuestion.objects.create(
            session=session,
            question_text='Здравствуйте! Опишите, пожалуйста, вашу проблему.',
            order_number=1,
            source=SessionQuestion.Source.SYSTEM
        )
        return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)

class SendMessageView(APIView):
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id, patient=request.user.patient)
        if session.status != Session.Status.IN_PROGRESS:
            return Response({'error': 'Сессия завершена'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем ответ на последний вопрос
        last_question = session.questions.filter(answer_text__isnull=True).last()
        if last_question:
            last_question.answer_text = serializer.validated_data['content']
            last_question.answered_at = timezone.now()
            last_question.save()

        # ИИ-заглушка
        try:
            ai_response = process_user_message(session, serializer.validated_data['content'])
        except NotImplementedError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Сохраняем вопрос от ИИ (заглушка)
        SessionQuestion.objects.create(
            session=session,
            question_text=ai_response.get('reply', 'Уточните, пожалуйста...'),
            order_number=session.questions.count() + 1,
            source=SessionQuestion.Source.AI
        )
        
        return Response(SessionSerializer(session).data)