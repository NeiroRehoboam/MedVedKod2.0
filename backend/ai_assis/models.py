from django.db import models
from django.utils import timezone
from patients.models import Patient

class BaseQuestion(models.Model):
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    is_multiple_choice = models.BooleanField(default=False)
    def __str__(self): return self.text[:50]

class BaseQuestionOption(models.Model):
    question = models.ForeignKey(BaseQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    def __str__(self): return self.text

class Session(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'В процессе'
        COMPLETED = 'COMPLETED', 'Завершена'
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    created_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"Сессия #{self.id} — {self.title or 'Без названия'}"

class SessionQuestion(models.Model):
    class Source(models.TextChoices):
        SYSTEM = 'SYSTEM', 'Система'
        AI = 'AI', 'ИИ'
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer_text = models.TextField(blank=True, null=True)
    order_number = models.PositiveIntegerField()
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.SYSTEM)
    allow_custom_answer = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    answered_at = models.DateTimeField(null=True, blank=True)