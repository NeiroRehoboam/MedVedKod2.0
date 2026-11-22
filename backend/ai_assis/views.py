from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db import transaction

from .models import (
    Session, SessionQuestion, SessionAnswer,
    BaseQuestion, BaseQuestionOption, Message
)
from .serializers import (
    SessionListSerializer,
    SessionDetailSerializer,
    SessionResultSerializer,
    StartSessionRequestSerializer,
    StartSessionResponseSerializer,
    SendMessageRequestSerializer,
    SendMessageResponseSerializer,
    SessionQuestionWithOptionsSerializer,
    MessageSerializer,
    BaseQuestionOptionSerializer,
)


@extend_schema(tags=['AI Sessions'])
class StartSessionView(APIView):
    """
    Создание новой сессии (обращения).
    Создаётся для текущего авторизованного пользователя.
    Возвращает id, название и статус.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=StartSessionRequestSerializer,
        responses={201: StartSessionResponseSerializer}
    )
    def post(self, request):
        serializer = StartSessionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        title = serializer.validated_data['title']

        session = Session.objects.create(
            user=request.user,
            title=title,
            status=Session.Status.IN_PROGRESS,
        )

        # Опционально: создаём системные вопросы из справочника
        questions = BaseQuestion.objects.filter(is_active=True).order_by('order')
        for q in questions:
            SessionQuestion.objects.create(
                session=session,
                question_text=q.text,
                order_number=q.order,
                source=SessionQuestion.Source.SYSTEM,
                allow_custom_answer=True,
            )

        return Response({
            "session_id": session.id,
            "title": session.title,
            "status": session.status,
            "status_display": session.get_status_display(),
            "created_at": session.created_at,
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['AI Sessions'])
class SendMessageView(APIView):
    """
    Отправка сообщения/ответа в сессии.
    
    В одном запросе можно:
    - отправить свободное сообщение (поле message)
    - ИЛИ ответить на конкретный вопрос (question_id + option_id или custom_answer)
    
    В ответе приходят:
    - сохранённое сообщение пользователя
    - ответ ИИ (заглушка)
    - следующие вопросы с опциями (чтобы не делать отдельный запрос)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SendMessageRequestSerializer,
        responses={200: SendMessageResponseSerializer}
    )
    def post(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id, user=request.user)
        except Session.DoesNotExist:
            return Response({'error': 'Сессия не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if session.status != Session.Status.IN_PROGRESS:
            return Response(
                {'error': 'Сессия уже завершена или отменена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SendMessageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        with transaction.atomic():
            user_message = None
            message_text = (data.get('message') or data.get('custom_answer') or '').strip()
            if message_text:
                user_message = Message.objects.create(
                    session=session,
                    role=Message.Role.USER,
                    content=message_text,
                )

            question_id = data.get('question_id')
            if question_id:
                try:
                    sq = SessionQuestion.objects.get(id=question_id, session=session)
                except SessionQuestion.DoesNotExist:
                    return Response({'error': 'Вопрос не найден в этой сессии'}, status=404)

                answer = SessionAnswer.objects.create(
                    question=sq,
                    custom_text=data.get('custom_answer'),
                )
                if data.get('option_id'):
                    try:
                        option = BaseQuestionOption.objects.get(id=data['option_id'])
                        answer.selected_option = option
                        answer.save()
                    except BaseQuestionOption.DoesNotExist:
                        pass

                sq.is_answered = True
                sq.save()

            # 3. Генерируем ответ ИИ (заглушка)
            ai_text = self._generate_ai_response(session, message_text)
            ai_message = Message.objects.create(
                session=session,
                role=Message.Role.ASSISTANT,
                content=ai_text,
            )

            next_questions = SessionQuestion.objects.filter(
                session=session,
                is_answered=False,
            ).order_by('order_number')
            next_questions_data = SessionQuestionWithOptionsSerializer(next_questions, many=True).data

        return Response({
            'user_message': MessageSerializer(user_message).data if user_message else None,
            'ai_response': MessageSerializer(ai_message).data,
            'next_questions': next_questions_data,
            'session_status': session.status,
        }, status=status.HTTP_200_OK)

    def _generate_ai_response(self, session, user_text):
        """Заглушка генерации ответа ИИ. Здесь будет вызов вашего LLM API."""
        if not user_text:
            return "Пожалуйста, ответьте на вопрос или опишите симптомы."
        return (
            f"Спасибо за информацию. Я зафиксировал: '{user_text}'. "
            f"В реальной версии здесь будет анализ симптомов и следующий вопрос от ИИ."
        )


@extend_schema(tags=['AI Sessions'])
class CompleteSessionView(APIView):
    """
    Завершение сессии и получение результата.
    Генерирует резюме и рекомендацию (заглушка), меняет статус на 'completed'.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: SessionResultSerializer}
    )
    def post(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id, user=request.user)
        except Session.DoesNotExist:
            return Response({'error': 'Сессия не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if session.status == Session.Status.COMPLETED:
            return Response({'error': 'Сессия уже завершена'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Заглушка: генерируем резюме на основе ответов
            answers = SessionAnswer.objects.filter(question__session=session).select_related('selected_option')
            answers_summary = []
            for a in answers:
                if a.selected_option:
                    answers_summary.append(f"{a.question.question_text}: {a.selected_option.text}")
                elif a.custom_text:
                    answers_summary.append(f"{a.question.question_text}: {a.custom_text}")

            session.summary = "Сводка ответов:\n" + "\n".join(answers_summary) if answers_summary else "Ответы не были даны."
            session.recommendation = (
                "На основании ваших ответов рекомендуется обратиться к терапевту. "
                "В реальной версии здесь будет рекомендация от ИИ."
            )
            session.status = Session.Status.COMPLETED
            session.save()

        return Response(SessionResultSerializer(session).data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(summary="Список сессий пользователя", responses={200: SessionListSerializer(many=True)}),
    retrieve=extend_schema(summary="Детали сессии", responses={200: SessionDetailSerializer}),
)
class SessionViewSet(viewsets.ModelViewSet):
    """
    CRUD для сессий текущего пользователя.
    Список (GET /) возвращает короткие карточки для главного экрана.
    Детали (GET /{id}/) возвращают полную сессию с вопросами и сообщениями.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return SessionListSerializer
        return SessionDetailSerializer

    def get_queryset(self):
        return Session.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)