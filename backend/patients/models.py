from django.db import models
from django.conf import settings
from consultations.crypto_module import encrypt_string, decrypt_string

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient', null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    diagnosis_encrypted = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.diagnosis_encrypted and not self.diagnosis_encrypted.startswith('gAAAAA'):
            self.diagnosis_encrypted = encrypt_string(self.diagnosis_encrypted)
        super().save(*args, **kwargs)

    @property
    def diagnosis(self): return decrypt_string(self.diagnosis_encrypted)
    def __str__(self): return f"{self.last_name} {self.first_name}"