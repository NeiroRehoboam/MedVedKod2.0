from rest_framework import serializers
from .models import (
    Session, SessionQuestion, SessionAnswer,
    BaseQuestion, BaseQuestionOption, Message
)

class BaseQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseQuestionOption
        fields = ['id', 'text', 'value', 'order']


class SessionListSerializer(serializers.ModelSerializer):
    """Короткий сериализатор для списка сессий на главном экране"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ['id', 'title', 'status', 'status_display', 'created_at', 'created_at_formatted']

    def get_created_at_formatted(self, obj):
        """Форматирование даты как на скриншоте: '10 ноября 2026'"""
        months = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        d = obj.created_at
        return f"{d.day} {months[d.month]} {d.year}"


class StartSessionRequestSerializer(serializers.Serializer):
    """Запрос на создание сессии"""
    title = serializers.CharField(
        max_length=255,
        help_text="Тема обращения (например, 'Головная боль')"
    )


class StartSessionResponseSerializer(serializers.Serializer):
    """Ответ после создания сессии"""
    session_id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    created_at = serializers.DateTimeField()

class SessionQuestionWithOptionsSerializer(serializers.ModelSerializer):
    """Вопрос сессии вместе с вариантами ответов из справочника"""
    options = serializers.SerializerMethodField()
    allow_custom_answer = serializers.BooleanField()

    class Meta:
        model = SessionQuestion
        fields = ['id', 'question_text', 'order_number', 'options', 'allow_custom_answer', 'is_answered']

    def get_options(self, obj):
        """Ищем базовый вопрос по тексту и возвращаем его варианты"""
        base_q = BaseQuestion.objects.filter(text=obj.question_text, is_active=True).first()
        if base_q:
            return BaseQuestionOptionSerializer(base_q.options.all(), many=True).data
        return []


class SendMessageRequestSerializer(serializers.Serializer):
    """
    Запрос на отправку сообщения/ответа.
    Можно ответить текстом ИЛИ выбрать вариант (или оба сразу).
    """
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Текстовое сообщение от пользователя (свободный ответ)"
    )
    question_id = serializers.IntegerField(
        required=False,
        help_text="ID вопроса, на который даётся ответ"
    )
    option_id = serializers.IntegerField(
        required=False,
        help_text="ID выбранного варианта ответа (если ответ из списка)"
    )
    custom_answer = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Свой текст ответа (если allow_custom_answer=True у вопроса)"
    )


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at']


class SendMessageResponseSerializer(serializers.Serializer):
    """
    Полный ответ на сообщение:
    - сообщение пользователя
    - ответ ИИ
    - следующие вопросы с опциями (чтобы не делать отдельный запрос)
    """
    user_message = MessageSerializer()
    ai_response = MessageSerializer()
    next_questions = SessionQuestionWithOptionsSerializer(many=True)
    session_status = serializers.CharField()


class SessionAnswerSerializer(serializers.ModelSerializer):
    option_text = serializers.CharField(source='selected_option.text', read_only=True, default=None)
    option_value = serializers.CharField(source='selected_option.value', read_only=True, default=None)

    class Meta:
        model = SessionAnswer
        fields = ['id', 'question', 'selected_option', 'option_text', 'option_value', 'custom_text', 'created_at']


class SessionResultSerializer(serializers.ModelSerializer):
    """Полный результат завершённой сессии"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    answers = SessionAnswerSerializer(source='questions.answers', many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'status', 'status_display',
            'summary', 'recommendation',
            'created_at', 'updated_at',
            'answers', 'messages'
        ]

class SessionDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    questions = SessionQuestionWithOptionsSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'status', 'status_display',
            'summary', 'recommendation',
            'created_at', 'updated_at',
            'questions', 'messages'
        ]