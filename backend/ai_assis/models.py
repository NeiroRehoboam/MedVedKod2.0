from django.db import models
from django.utils import timezone
from consultations.crypto_module import decrypt_field, encrypt_field
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
    question_text_encrypted = models.TextField()
    answer_text_encrypted = models.TextField(blank=True, null=True)
    order_number = models.PositiveIntegerField()
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.SYSTEM)
    allow_custom_answer = models.BooleanField(default=True)
    options = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    answered_at = models.DateTimeField(null=True, blank=True)

    @property
    def _encryption_identity(self):
        return f'session:{self.session_id}'

    @property
    def question_text(self):
        return decrypt_field(self.question_text_encrypted, self._encryption_identity)

    @question_text.setter
    def question_text(self, value):
        self.question_text_encrypted = encrypt_field(value, self._encryption_identity)

    @property
    def answer_text(self):
        return decrypt_field(self.answer_text_encrypted, self._encryption_identity)

    @answer_text.setter
    def answer_text(self, value):
        self.answer_text_encrypted = encrypt_field(value, self._encryption_identity)
