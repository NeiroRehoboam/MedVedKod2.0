from django.db import models
from patients.models import Patient

class Consultation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('completed', 'Завершена'),
        ('emergency', 'Экстренная госпитализация'),
    ]
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE,
        related_name='consultations', verbose_name="Пациент"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")
    ai_summary = models.TextField(blank=True, null=True, verbose_name="Заключение ИИ")
    emergency_reason = models.TextField(blank=True, null=True, verbose_name="Причина экстренности")

    class Meta:
        verbose_name = "Консультация"
        verbose_name_plural = "Консультации"
        ordering = ['-created_at']

    def __str__(self):
        return f"Консультация #{self.id} — {self.patient}"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'ИИ-ассистент'),
        ('system', 'Система'),
    ]
    consultation = models.ForeignKey(
        Consultation, on_delete=models.CASCADE,
        related_name='messages', verbose_name="Консультация"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Роль")
    content = models.TextField(verbose_name="Текст сообщения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    is_emergency = models.BooleanField(default=False, verbose_name="Экстренный симптом")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."