from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Session, SessionQuestion, BaseQuestion
from .serializers import (SessionSerializer, SendMessageSerializer, 
                          BaseQuestionSerializer, BaseQuestionOptionSerializer)
from .services import process_user_message
from dictionaries.models import ComplaintCategory
from dictionaries.serializers import ComplaintCategorySerializer

class BaseQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BaseQuestion.objects.filter(is_active=True).order_by('order')
    serializer_class = BaseQuestionSerializer

class StartSessionView(APIView):
    def post(self, request):
        try:
            patient = request.user.patient
        except Exception:
            return Response({'error': 'Нет карты пациента'}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем сессию, но пока не задаем вопрос
        session = Session.objects.create(patient=patient)

        # Отдаем список категорий для выбора
        categories = ComplaintCategory.objects.filter(active=True)
        return Response({
            "session_id": session.id,
            "status": session.status,
            "step": "choose_category",
            "categories": ComplaintCategorySerializer(categories, many=True).data
        }, status=status.HTTP_201_CREATED)

class SelectCategoryView(APIView):
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id, patient=request.user.patient)
        
        category_id = request.data.get('category_id')
        if not category_id:
            return Response({'error': 'Не передана категория'}, status=status.HTTP_400_BAD_REQUEST)

        category = get_object_or_404(ComplaintCategory, id=category_id)

        # Ищем первый вопрос, привязанный к этой категории (если есть)
        # В BaseQuestion поле category хранит код (например, 'TRAUMA')
        first_q = BaseQuestion.objects.filter(
            is_active=True, 
            category=category.code, 
            order=1
        ).first()
        
        # Если нет специфичного, берем общий первый вопрос
        if not first_q:
            first_q = BaseQuestion.objects.filter(is_active=True, order=1).first()

        if not first_q:
            return Response({'error': 'Нет вопросов в БД'}, status=500)

        # Создаем первый вопрос в сессии
        sq = SessionQuestion.objects.create(
            session=session,
            question_text=first_q.text,
            order_number=1,
            source=SessionQuestion.Source.SYSTEM
        )

        return Response({
            "session_id": session.id,
            "status": session.status,
            "question": {
                "id": sq.id,
                "text": first_q.text,
                "options": BaseQuestionOptionSerializer(first_q.options.all(), many=True).data
            }
        }, status=status.HTTP_200_OK)

class SendMessageView(APIView):
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id, patient=request.user.patient)
        if session.status != Session.Status.IN_PROGRESS:
            return Response({'error': 'Сессия завершена', 'status': session.status}, status=400)

        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user_text = serializer.validated_data['content']
        last_q = session.questions.filter(answer_text__isnull=True).last()
        if last_q:
            last_q.answer_text = user_text
            last_q.answered_at = timezone.now()
            last_q.save()

        answered_count = session.questions.filter(answer_text__isnull=False).count()
        total_base = BaseQuestion.objects.filter(is_active=True).count()

        if answered_count < total_base:
            next_q = BaseQuestion.objects.filter(is_active=True, order__gt=answered_count).order_by('order').first()
            if next_q:
                SessionQuestion.objects.create(session=session, question_text=next_q.text, order_number=session.questions.count()+1, source=SessionQuestion.Source.SYSTEM)
        else:
            try:
                ai_resp = process_user_message(session, user_text, history=[])
                reply = ai_resp['reply']
            except NotImplementedError:
                reply = 'Спасибо! Ваши ответы записаны. Врач ознакомится с ними.'
            
            SessionQuestion.objects.create(session=session, question_text=reply, order_number=session.questions.count()+1, source=SessionQuestion.Source.AI)
            session.status = Session.Status.COMPLETED
            session.finished_at = timezone.now()
            session.save()

        return Response(SessionSerializer(session).data, status=200)