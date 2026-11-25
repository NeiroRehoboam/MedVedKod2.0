from django.db import models
from django.conf import settings
from consultations.crypto_module import encrypt_string, decrypt_string
from dictionaries.models import PaymentType

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient', null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    diagnosis_encrypted = models.TextField(blank=True, null=True)
    preferred_payment = models.ForeignKey(
        PaymentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients',
        verbose_name='Приоритетная оплата',
    )
    registration_date = models.DateTimeField(auto_now_add=True)

    @property
    def _encryption_identity(self):
        return f'user:{self.user_id}' if self.user_id else 'orphan'

    @property
    def diagnosis(self):
        return decrypt_string(self.diagnosis_encrypted, self._encryption_identity)

    @diagnosis.setter
    def diagnosis(self, value):
        self.diagnosis_encrypted = encrypt_string(value, self._encryption_identity) if value else None

    def __str__(self): return f"{self.last_name} {self.first_name}"
