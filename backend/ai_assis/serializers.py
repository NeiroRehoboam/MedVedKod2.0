from rest_framework import serializers
from .models import Session, SessionQuestion, BaseQuestion, BaseQuestionOption


class BaseQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseQuestionOption
        fields = ['id', 'text', 'order']


class SessionQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    question_text = serializers.CharField()
    answer_text = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = SessionQuestion
        fields = [
            'id', 'question_text', 'order_number', 'answer_text',
            'source', 'allow_custom_answer', 'options',
        ]

    def get_options(self, obj):
        base_q = BaseQuestion.objects.filter(text=obj.question_text, is_active=True).first()
        return BaseQuestionOptionSerializer(base_q.options.all(), many=True).data if base_q else []


class SessionListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'title', 'status', 'status_display', 'created_at', 'summary']

    def get_summary(self, obj):
        first = obj.questions.exclude(
            answer_text_encrypted__isnull=True
        ).exclude(answer_text_encrypted='').first()
        return first.answer_text[:60] + '...' if first else 'Нет ответов'


class SessionDetailSerializer(serializers.ModelSerializer):
    questions = SessionQuestionSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'status', 'status_display',
            'created_at', 'finished_at', 'questions',
        ]


class SafetyStatusSerializer(serializers.Serializer):
    danger_status = serializers.ChoiceField(
        choices=['dangerous', 'uncertain', 'no_critical_signs_detected']
    )
    is_dangerous = serializers.BooleanField()
    urgency = serializers.CharField()
    reason = serializers.CharField()
    matched_signs = serializers.ListField(child=serializers.CharField())
    recommended_action = serializers.CharField()
    should_stop = serializers.BooleanField()


class RoutingSummarySerializer(serializers.Serializer):
    urgency = serializers.CharField()
    justification = serializers.CharField()
    recommendations = serializers.CharField()


class AiSessionResponseSerializer(serializers.Serializer):
    """Единая форма ответа для всех эндпоинтов AI-сессий."""

    status = serializers.CharField()
    session = SessionDetailSerializer()
    questions = SessionQuestionSerializer(many=True)
    ai_questions = SessionQuestionSerializer(many=True)
    next_question = SessionQuestionSerializer(allow_null=True, required=False)
    safety = SafetyStatusSerializer()
    recommendation = serializers.DictField(required=False)
    routing = RoutingSummarySerializer(required=False)
    message = serializers.CharField(required=False)


class SessionResultSerializer(AiSessionResponseSerializer):
    """Сохранённый результат завершённой сессии (только чтение)."""


class SendMessageRequestSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=4000, trim_whitespace=True)
    question_id = serializers.IntegerField(required=False, min_value=1)


class SendMessageResponseSerializer(AiSessionResponseSerializer):
    pass


class UpdateAnswerRequestSerializer(serializers.Serializer):
    """Запрос на исправление уже данного ответа в незавершённой сессии."""

    answer_text = serializers.CharField(max_length=4000, trim_whitespace=True)


class CompleteRequestSerializer(serializers.Serializer):
    """Эндпоинт завершения намеренно не принимает данные."""
