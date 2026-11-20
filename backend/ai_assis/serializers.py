from rest_framework import serializers
from .models import Consultation, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'is_emergency', 'created_at']
        read_only_fields = ['id', 'created_at']


class ConsultationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Consultation
        fields = ['id', 'patient', 'status', 'created_at', 'updated_at', 'ai_summary', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at', 'ai_summary']


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=2000)