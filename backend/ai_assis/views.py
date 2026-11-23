from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from patients.models import Patient
from routing.models import RoutingResult
from dictionaries.models import Specialty

from .models import BaseQuestion, BaseQuestionOption, Session, SessionQuestion
from .serializers import (
    AiSessionResponseSerializer,
    RoutingSummarySerializer,
    SendMessageRequestSerializer,
    SendMessageResponseSerializer,
    SessionDetailSerializer,
    SessionListSerializer,
    SessionQuestionSerializer,
)
from .services import (
    check_message_safety,
    choose_worst_safety,
    generate_next_questions,
    generate_recommendation,
    get_session_safety,
    map_urgency,
    to_text,
)

DEFAULT_BASE_QUESTION = "Что с тобой случилось?"
DEFAULT_BASE_OPTIONS = (
    "Болит голова",
    "Болит грудь",
    "Температура",
    "Насморк или кашель",
    "Боль в животе",
    "Другое",
)


def _get_session(request, session_id: int) -> Session:
    """Only the owner can access a session."""
    patient = get_object_or_404(Patient, user=request.user)
    return get_object_or_404(Session, id=session_id, patient=patient)


def _ordered_questions(session) -> list:
    return list(session.questions.order_by('order_number', 'id'))


def _ai_questions(session):
    """The six generated questions, stored in DB and re-sent on every response."""
    return list(session.questions.filter(source=SessionQuestion.Source.AI).order_by('order_number', 'id'))


def _next_question(session) -> SessionQuestion | None:
    unanswered = session.questions.filter(answer_text__isnull=True).order_by('order_number', 'id')
    return unanswered.filter(source=SessionQuestion.Source.SYSTEM).first() or unanswered.first()


def _session_response(
    session,
    status_value: str,
    safety: dict,
    next_question=None,
    recommendation: dict | None = None,
    routing=None,
    message: str | None = None,
    response_status: int = status.HTTP_200_OK,
) -> Response:
    """One response shape for all AI-session endpoints."""
    data = {
        'status': status_value,
        'session': SessionDetailSerializer(session).data,
        'questions': SessionQuestionSerializer(_ordered_questions(session), many=True).data,
        'ai_questions': SessionQuestionSerializer(_ai_questions(session), many=True).data,
        'safety': safety,
    }
    if next_question is not None:
        data['next_question'] = SessionQuestionSerializer(next_question).data
    if recommendation is not None:
        data['recommendation'] = recommendation
    if routing is not None:
        data['routing'] = RoutingSummarySerializer(routing).data
    if message is not None:
        data['message'] = message
    return Response(data, status=response_status)


def _find_specialty(name: str | None):
    if not name or not isinstance(name, str) or not name.strip():
        return None
    matches = Specialty.objects.filter(name__icontains=name.strip()[:100])
    return matches.first() if matches.count() == 1 else None


def _save_routing(session, safety: dict, recommendation: dict) -> RoutingResult:
    urgency = safety['urgency'] if safety['should_stop'] else recommendation.get('urgency')
    routing, _ = RoutingResult.objects.update_or_create(
        session=session,
        defaults={
            'urgency': map_urgency(urgency),
            'specialty': _find_specialty(recommendation.get('doctor')),
            'justification': to_text(recommendation.get('justification')) or safety['reason'],
            'recommendations': to_text(recommendation.get('recommendation')) or safety['recommended_action'],
        },
    )
    return routing


@extend_schema(tags=['AI Sessions'])
class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Session.objects.filter(patient__user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        return SessionListSerializer if self.action == 'list' else SessionDetailSerializer

    @extend_schema(responses={200: AiSessionResponseSerializer})
    def retrieve(self, request, *args, **kwargs):
        session = self.get_object()
        return _session_response(
            session,
            session.status,
            get_session_safety(session),
            next_question=_next_question(session),
        )


@extend_schema(tags=['AI Sessions'])
class StartSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses={201: AiSessionResponseSerializer})
    def post(self, request):
        patient, _ = Patient.objects.get_or_create(user=request.user)

        session = Session.objects.create(patient=patient, title="Новое обращение")

        if not BaseQuestion.objects.filter(is_active=True).exists():
            base = BaseQuestion.objects.create(
                text=DEFAULT_BASE_QUESTION,
                order=1,
                is_multiple_choice=True,
            )
            for index, option in enumerate(DEFAULT_BASE_OPTIONS, start=1):
                BaseQuestionOption.objects.create(question=base, text=option, order=index)

        questions = BaseQuestion.objects.filter(is_active=True).order_by('order')
        for q in questions:
            SessionQuestion.objects.create(
                session=session,
                question_text=q.text,
                order_number=q.order,
                source=SessionQuestion.Source.SYSTEM,
                allow_custom_answer=not q.is_multiple_choice,
            )

        return _session_response(
            session,
            Session.Status.IN_PROGRESS,
            get_session_safety(session),
            next_question=_next_question(session),
            response_status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=['AI Sessions'])
class InitialQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: AiSessionResponseSerializer})
    def get(self, request, session_id):
        session = _get_session(request, session_id)
        return _session_response(
            session,
            session.status,
            get_session_safety(session),
            next_question=_next_question(session),
        )


@extend_schema(tags=['AI Sessions'])
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SendMessageRequestSerializer,
        responses={200: SendMessageResponseSerializer},
    )
    def post(self, request, session_id):
        session = _get_session(request, session_id)
        if session.status != Session.Status.IN_PROGRESS:
            return Response({'error': 'Сессия завершена'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SendMessageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_text = serializer.validated_data['content']
        question_id = serializer.validated_data.get('question_id')

        if question_id is not None:
            question = session.questions.filter(id=question_id).first()
            if question is None:
                return Response({'error': 'Вопрос не относится к этой сессии'}, status=status.HTTP_400_BAD_REQUEST)
            if question.answer_text not in (None, ''):
                return Response({'error': 'На вопрос уже дан ответ'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            question = _next_question(session)

        if question is None:
            return Response(
                {'error': 'Все вопросы отвечены. Вызовите /complete/ для завершения опроса.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        question.answer_text = user_text
        question.answered_at = timezone.now()
        question.save(update_fields=['answer_text', 'answered_at'])

        # Every answer is checked, including answers to the AI questions.
        # The full history is re-checked as well so a sign missed earlier
        # still stops the survey.
        safety = choose_worst_safety(
            check_message_safety(user_text),
            get_session_safety(session, use_llm=False),
        )

        if safety['should_stop']:
            recommendation = {
                'source': 'safety_check',
                'recommendation': safety['recommended_action'],
                'justification': safety['reason'],
                'urgency': safety['urgency'],
                'doctor': '',
                'place': '',
                'evidence': [],
            }
            routing = _save_routing(session, safety, recommendation)
            session.status = Session.Status.COMPLETED
            session.finished_at = timezone.now()
            session.save(update_fields=['status', 'finished_at'])
            return _session_response(
                session,
                Session.Status.COMPLETED,
                safety,
                recommendation=recommendation,
                routing=routing,
                message=safety['recommended_action'],
            )

        # Generate the six follow-up questions once, then simply re-send the
        # stored copies with every subsequent answer (no extra endpoint).
        if not _ai_questions(session):
            max_order = max([q.order_number for q in _ordered_questions(session)] or [0])
            SessionQuestion.objects.bulk_create([
                SessionQuestion(
                    session=session,
                    question_text=text,
                    order_number=max_order + index,
                    source=SessionQuestion.Source.AI,
                    allow_custom_answer=True,
                )
                for index, text in enumerate(generate_next_questions(session), start=1)
            ])

        ai_questions = _ai_questions(session)
        next_question = next(
            (q for q in ai_questions if q.answer_text in (None, '')),
            None,
        ) or _next_question(session)

        return _session_response(
            session,
            Session.Status.IN_PROGRESS,
            safety,
            next_question=next_question,
        )


@extend_schema(tags=['AI Sessions'])
class CompleteSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: AiSessionResponseSerializer})
    def post(self, request, session_id):
        session = _get_session(request, session_id)

        if not any(q.answer_text for q in _ordered_questions(session)):
            return Response({'error': 'Нет ответов пациента'}, status=status.HTTP_400_BAD_REQUEST)

        safety = get_session_safety(session, use_llm=True)
        recommendation = generate_recommendation(session, safety)
        routing = _save_routing(session, safety, recommendation)

        session.status = Session.Status.COMPLETED
        session.finished_at = session.finished_at or timezone.now()
        session.save(update_fields=['status', 'finished_at'])

        return _session_response(
            session,
            Session.Status.COMPLETED,
            safety,
            recommendation=recommendation,
            routing=routing,
        )
