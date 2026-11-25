from django.db import models
from ai_assis.models import Session
from consultations.crypto_module import decrypt_field, encrypt_field
from dictionaries.models import Specialty

class RoutingResult(models.Model):
    class Urgency(models.TextChoices):
        EMERGENCY = 'EMERGENCY', 'Экстренно'; URGENT = 'URGENT', 'Срочно'; PLANNED = 'PLANNED', 'Планово'; SELF_HELP = 'SELF_HELP', 'Самопомощь'
    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='routing_result')
    urgency = models.CharField(max_length=20, choices=Urgency.choices)
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, null=True, blank=True)
    justification_encrypted = models.TextField()
    recommendations_encrypted = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def _encryption_identity(self):
        return f'session:{self.session_id}'

    @property
    def justification(self):
        return decrypt_field(self.justification_encrypted, self._encryption_identity)

    @justification.setter
    def justification(self, value):
        self.justification_encrypted = encrypt_field(value, self._encryption_identity)

    @property
    def recommendations(self):
        return decrypt_field(self.recommendations_encrypted, self._encryption_identity)

    @recommendations.setter
    def recommendations(self, value):
        self.recommendations_encrypted = encrypt_field(value, self._encryption_identity)
