from django.db import models
from patients.models import Patient

class BaseQuestion(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    is_multiple_choice = models.BooleanField(default=False)
    def __str__(self): return self.text

class BaseQuestionOption(models.Model):
    question = models.ForeignKey(BaseQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    def __str__(self): return self.text

class Session(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'В процессе'
        COMPLETED = 'COMPLETED', 'Завершена'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
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