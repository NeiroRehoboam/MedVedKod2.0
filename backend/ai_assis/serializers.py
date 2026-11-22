from rest_framework import serializers
from .models import BaseQuestion, BaseQuestionOption, Session, SessionQuestion

class BaseQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseQuestionOption
        fields = ['id', 'text', 'order']

class BaseQuestionSerializer(serializers.ModelSerializer):
    options = BaseQuestionOptionSerializer(many=True, read_only=True)
    class Meta:
        model = BaseQuestion
        fields = ['id', 'text', 'order', 'is_multiple_choice', 'options']

class SessionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionQuestion
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    questions = SessionQuestionSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Session
        fields = ['id', 'status', 'status_display', 'created_at', 'finished_at', 'questions']
        read_only_fields = ['id', 'status', 'created_at', 'finished_at']

class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=2000)