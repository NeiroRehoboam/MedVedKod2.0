from rest_framework import serializers
from .models import Session, SessionQuestion, BaseQuestion, BaseQuestionOption

class BaseQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta: model = BaseQuestionOption; fields = ['id', 'text', 'order']

class SessionQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    class Meta:
        model = SessionQuestion
        fields = ['id', 'question_text', 'order_number', 'answer_text', 'source', 'allow_custom_answer', 'options']
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
        first = obj.questions.exclude(answer_text__isnull=True).exclude(answer_text='').first()
        return first.answer_text[:60] + '...' if first else 'Нет ответов'

class SessionDetailSerializer(serializers.ModelSerializer):
    questions = SessionQuestionSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Session
        fields = ['id', 'title', 'status', 'status_display', 'created_at', 'finished_at', 'questions']

class SendMessageRequestSerializer(serializers.Serializer):
    content = serializers.CharField(help_text="Текст ответа")
    question_id = serializers.IntegerField(required=False)

class SendMessageResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField(required=False)
    next_question = SessionQuestionSerializer(required=False)
    session = SessionDetailSerializer(required=False)