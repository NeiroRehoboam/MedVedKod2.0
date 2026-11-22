from django.db import models
from django.utils import timezone
from django.conf import settings


class BaseQuestion(models.Model):
    """Базовый шаблон вопроса (системный справочник)"""
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Базовый вопрос'
        verbose_name_plural = 'Базовые вопросы'

    def __str__(self):
        return f"Вопрос #{self.order}: {self.text[:50]}"


class BaseQuestionOption(models.Model):
    """Варианты ответов для базового вопроса"""
    question = models.ForeignKey(BaseQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255, verbose_name="Текст варианта")
    value = models.CharField(max_length=100, verbose_name="Значение")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.text} ({self.value})"


class Session(models.Model):
    """Сессия опроса (обращение пациента)"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_sessions',
        verbose_name="Пользователь"
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.SET_NULL,
        related_name='ai_sessions',
        null=True,
        blank=True,
        verbose_name="Карта пациента"
    )
    title = models.CharField(max_length=255, verbose_name="Тема обращения")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        verbose_name="Статус"
    )
    summary = models.TextField(blank=True, null=True, verbose_name="Резюме")
    recommendation = models.TextField(blank=True, null=True, verbose_name="Рекомендация")

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class SessionQuestion(models.Model):
    """Вопрос в рамках конкретной сессии"""
    class Source(models.TextChoices):
        SYSTEM = 'system', 'Системный'
        AI_GENERATED = 'ai_generated', 'Сгенерирован ИИ'

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField(verbose_name="Текст вопроса")
    order_number = models.PositiveIntegerField(verbose_name="Порядковый номер")
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.SYSTEM)
    # Позволяет ли пользователь ввести свой ответ (не только из вариантов)
    allow_custom_answer = models.BooleanField(default=True)
    # Статус вопроса
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order_number', 'id']

    def __str__(self):
        return f"Вопрос #{self.order_number} в сессии #{self.session_id}"


class SessionAnswer(models.Model):
    """Ответ пациента на вопрос сессии"""
    question = models.ForeignKey(SessionQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_option = models.ForeignKey(
        BaseQuestionOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Выбранный вариант"
    )
    custom_text = models.TextField(blank=True, null=True, verbose_name="Свой ответ")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.selected_option:
            return f"Ответ на вопрос #{self.question.order_number}: {self.selected_option.text}"
        return f"Ответ на вопрос #{self.question.order_number}: {self.custom_text}"


class Message(models.Model):
    """Сообщение в диалоге с ИИ"""
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ASSISTANT = 'assistant', 'Ассистент'
        SYSTEM = 'system', 'Система'

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return