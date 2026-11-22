from django.db import models
from ai_assis.models import Session
from dictionaries.models import Specialty

class RoutingResult(models.Model):
    class Urgency(models.TextChoices):
        EMERGENCY = 'EMERGENCY', 'Экстренно'
        URGENT = 'URGENT', 'Срочно'
        PLANNED = 'PLANNED', 'Планово'
        SELF_HELP = 'SELF_HELP', 'Самопомощь'

    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='routing_result')
    urgency = models.CharField(max_length=20, choices=Urgency.choices)
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, null=True, blank=True)
    justification = models.TextField(verbose_name="Обоснование")
    recommendations = models.TextField(verbose_name="Рекомендации")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Маршрут #{self.id} (Сессия {self.session_id})"