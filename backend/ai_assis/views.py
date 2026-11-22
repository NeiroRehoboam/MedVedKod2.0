from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from .models import Session, SessionQuestion, BaseQuestion
from .serializers import (
    SessionListSerializer, SessionDetailSerializer, 
    SessionQuestionSerializer, SendMessageRequestSerializer, 
    SendMessageResponseSerializer
)
from .services import process_user_message
from patients.models import Patient

@extend_schema(tags=['AI Sessions'])
class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return Session.objects.filter(patient__user=self.request.user).order_by('-created_at')
    def get_serializer_class(self):
        return SessionListSerializer if self.action == 'list' else SessionDetailSerializer

@extend_schema(tags=['AI Sessions'])
class StartSessionView(APIView):
    @extend_schema(request=None, responses={201: SessionDetailSerializer})
    def post(self, request):
        # Автоматически создаем карту пациента, если ее нет
        patient, _ = Patient.objects.get_or_create(user=request.user)
        
        session = Session.objects.create(patient=patient, title="Новое обращение")
        
        questions = BaseQuestion.objects.filter(is_active=True).order_by('order')
        for q in questions:
            SessionQuestion.objects.create(
                session=session, question_text=q.text, order_number=q.order,
                source=SessionQuestion.Source.SYSTEM, allow_custom_answer=q.is_multiple_choice
            )
        
        return Response(SessionDetailSerializer(session).data, status=201)

@extend_schema(tags=['AI Sessions'])
class SendMessageView(APIView):
    @extend_schema(request=SendMessageRequestSerializer, responses={200: SendMessageResponseSerializer})
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id, patient=request.user.patient)
        if session.status != Session.Status.IN_PROGRESS:
            return Response({'error': 'Сессия завершена'}, status=400)

        serializer = SendMessageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user_text = serializer.validated_data['content']
        question_id = serializer.validated_data.get('question_id')

        q = session.questions.filter(id=question_id).first() if question_id else session.questions.filter(answer_text__isnull=True).first()
        if q:
            q.answer_text = user_text
            q.answered_at = timezone.now()
            q.save()

        unanswered = session.questions.filter(answer_text__isnull=True).count()
        
        if unanswered == 0:
            try:
                history = [{'role': 'user', 'content': q.answer_text} for q in session.questions.all()]
                ai_resp = process_user_message(session, user_text, history)
                reply = ai_resp['reply']
            except NotImplementedError:
                reply = 'Спасибо! Ваши ответы записаны.'
            
            session.status = Session.Status.COMPLETED
            session.finished_at = timezone.now()
            session.save()
            
            return Response({
                'status': 'COMPLETED',
                'message': reply,
                'session': SessionDetailSerializer(session).data
            }, status=200)

        # Возвращаем только один следующий вопрос
        next_q = session.questions.filter(answer_text__isnull=True).order_by('order_number').first()
        return Response({
            'status': 'IN_PROGRESS',
            'next_question': SessionQuestionSerializer(next_q).data if next_q else None,
            'session': SessionDetailSerializer(session).data
        }, status=200)