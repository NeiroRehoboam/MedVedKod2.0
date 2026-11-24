
import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from .models import Session, SessionQuestion, BaseQuestion
from .serializers import (
    SessionListSerializer,
    SessionDetailSerializer,
    SessionQuestionSerializer,
    SendMessageRequestSerializer,
    SendMessageResponseSerializer,
)
from .services import process_user_message
from patients.models import Patient


logger = logging.getLogger(__name__)

AI_QUESTIONS_LIMIT = 6


@extend_schema(tags=['AI Sessions'])
class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return Session.objects.filter(
            patient__user=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return SessionListSerializer
        return SessionDetailSerializer


@extend_schema(tags=['AI Sessions'])
class StartSessionView(APIView):

    @extend_schema(
        request=None,
        responses={201: SessionDetailSerializer},
    )
    def post(self, request):
        patient, _ = Patient.objects.get_or_create(user=request.user)

        initial_question = BaseQuestion.objects.filter(
            is_active=True
        ).order_by('order').first()

        if initial_question is None:
            return Response(
                {'error': 'Не найден начальный вопрос анкеты.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        session = Session.objects.create(
            patient=patient,
            title='Новое обращение',
        )

        SessionQuestion.objects.create(
            session=session,
            question_text=initial_question.text,
            order_number=0,
            source=SessionQuestion.Source.SYSTEM,
            allow_custom_answer=True,
        )

        return Response(
            SessionDetailSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['AI Sessions'])
class SendMessageView(APIView):

    @extend_schema(
        request=SendMessageRequestSerializer,
        responses={200: SendMessageResponseSerializer},
    )
    def post(self, request, session_id):
        session = get_object_or_404(
            Session,
            id=session_id,
            patient__user=request.user,
        )

        if session.status != Session.Status.IN_PROGRESS:
            return Response(
                {'error': 'Сессия уже завершена.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SendMessageRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_text = serializer.validated_data['content'].strip()
        question_id = serializer.validated_data.get('question_id')

        if not user_text:
            return Response(
                {'error': 'Ответ не может быть пустым.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Находим вопрос, на который пользователь отвечает.
        if question_id is not None:
            question = session.questions.filter(id=question_id).first()

            if question is None:
                return Response(
                    {'error': 'Вопрос не принадлежит этой сессии.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            question = session.questions.filter(
                answer_text__isnull=True
            ).order_by('order_number').first()

        # Поддержка повторной отправки запроса после сбоя GigaChat.
        if question is None:
            question = session.questions.order_by(
                '-order_number'
            ).first()

            if question is None or question.answer_text != user_text:
                return Response(
                    {'error': 'Не найден вопрос для этого ответа.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif question.answer_text is not None:
            if question.answer_text != user_text:
                return Response(
                    {'error': 'На этот вопрос уже был дан другой ответ.'},
                    status=status.HTTP_409_CONFLICT,
                )

        else:
            question.answer_text = user_text
            question.answered_at = timezone.now()
            question.save(update_fields=['answer_text', 'answered_at'])

        # Если следующий вопрос уже создан, повторно его не генерируем.
        pending_question = session.questions.filter(
            answer_text__isnull=True
        ).order_by('order_number').first()

        if pending_question is not None:
            return Response({
                'status': 'IN_PROGRESS',
                'next_question': SessionQuestionSerializer(
                    pending_question
                ).data,
                'session': SessionDetailSerializer(session).data,
            })

        # История в формате, который ожидает rag_module.
        history = [
            {
                'question': item.question_text,
                'answer': item.answer_text,
            }
            for item in session.questions.filter(
                answer_text__isnull=False
            ).exclude(
                answer_text=''
            ).order_by('order_number')
        ]

        answered_ai_count = session.questions.filter(
            source=SessionQuestion.Source.AI,
            answer_text__isnull=False,
        ).count()

        # Импортируем RAG-функции только при необходимости.
        from rag_module import (
            generate_next_question,
            TriageBlockedError,
        )

        # Генерация шести дополнительных вопросов через GigaChat.
        if answered_ai_count < AI_QUESTIONS_LIMIT:
            try:
                generated = generate_next_question(history)

                question_text = generated['question']
                options = generated.get('options', [])

                last_order = session.questions.order_by(
                    '-order_number'
                ).first().order_number

                next_question = SessionQuestion.objects.create(
                    session=session,
                    question_text=question_text,
                    order_number=last_order + 1,
                    source=SessionQuestion.Source.AI,
                    allow_custom_answer=True,
                    options=options,
                )

                return Response({
                    'status': 'IN_PROGRESS',
                    'next_question': SessionQuestionSerializer(
                        next_question
                    ).data,
                    'session': SessionDetailSerializer(session).data,
                })

            except TriageBlockedError as error:
                triage_result = error.result

                if hasattr(triage_result, 'model_dump'):
                    triage_data = triage_result.model_dump()
                else:
                    triage_data = triage_result

                session.status = Session.Status.COMPLETED
                session.finished_at = timezone.now()
                session.save(update_fields=['status', 'finished_at'])

                return Response({
                    'status': 'COMPLETED',
                    'message': triage_data.get(
                        'message',
                        'Обнаружены признаки, требующие медицинской оценки.',
                    ),
                    'triage': triage_data,
                    'session': SessionDetailSerializer(session).data,
                })

            except Exception:
                logger.exception(
                    'Ошибка генерации следующего вопроса для сессии %s',
                    session.id,
                )
                return Response(
                    {
                        'error': (
                            'Не удалось сформировать следующий вопрос. '
                            'Попробуйте отправить ответ повторно.'
                        )
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        # После шести ответов ИИ запускаем итоговый RAG.
        try:
            ai_response = process_user_message(
                session,
                user_text,
                history,
            )

            recommendation = ai_response['recommendation']

            session.status = Session.Status.COMPLETED
            session.finished_at = timezone.now()
            session.save(update_fields=['status', 'finished_at'])

            return Response({
                'status': 'COMPLETED',
                'message': ai_response['reply'],
                'recommendation': recommendation,
                'session': SessionDetailSerializer(session).data,
            })

        except TriageBlockedError as error:
            triage_result = error.result

            if hasattr(triage_result, 'model_dump'):
                triage_data = triage_result.model_dump()
            else:
                triage_data = triage_result

            session.status = Session.Status.COMPLETED
            session.finished_at = timezone.now()
            session.save(update_fields=['status', 'finished_at'])

            return Response({
                'status': 'COMPLETED',
                'message': triage_data.get(
                    'message',
                    'Необходимо обратиться за медицинской помощью.',
                ),
                'triage': triage_data,
                'session': SessionDetailSerializer(session).data,
            })

        except ValueError as error:
            logger.warning(
                'Недостаточно данных для рекомендации, сессия %s: %s',
                session.id,
                error,
            )
            return Response(
                {
                    'error': (
                        'Не удалось сформировать рекомендацию '
                        'из-за недостатка данных.'
                    ),
                    'details': str(error),
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        except Exception:
            logger.exception(
                'Ошибка формирования рекомендации для сессии %s',
                session.id,
            )
            return Response(
                {
                    'error': (
                        'Не удалось сформировать рекомендацию. '
                        'Попробуйте повторить запрос.'
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
