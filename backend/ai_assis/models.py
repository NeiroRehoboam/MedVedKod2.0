from django.db import models
from patients.models import Patient

class Session(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'В процессе'
        COMPLETED = 'COMPLETED', 'Завершена'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True)

class SessionQuestion(models.Model):
    class Source(models.TextChoices):
        SYSTEM = 'SYSTEM', 'Система'
        AI = 'AI', 'ИИ'

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer_text = models.TextField(blank=True, null=True)
    order_number = models.IntegerField()
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.AI)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

class QuickAnswer(models.Model):
    question = models.ForeignKey(SessionQuestion, on_delete=models.CASCADE, related_name='quick_answers')
    text = models.TextField()
    order_number = models.IntegerField()