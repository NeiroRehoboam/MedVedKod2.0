from rest_framework import serializers
from .models import Session, SessionQuestion, QuickAnswer

class QuickAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickAnswer
        fields = '__all__'

class SessionQuestionSerializer(serializers.ModelSerializer):
    quick_answers = QuickAnswerSerializer(many=True, read_only=True)
    class Meta:
        model = SessionQuestion
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    questions = SessionQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Session
        fields = '__all__'

class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=2000)