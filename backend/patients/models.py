from django.db import models
from consultations.crypto_module import encrypt_string, decrypt_string

class Patient(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    birth_date = models.DateField(verbose_name="Дата рождения")
    diagnosis_encrypted = models.TextField(blank=True, null=True, verbose_name="Диагноз (зашифрован)")

    def save(self, *args, **kwargs):
        if self.diagnosis_encrypted and not self.diagnosis_encrypted.startswith('gAAAAA'):
            self.diagnosis_encrypted = encrypt_string(self.diagnosis_encrypted)
        super().save(*args, **kwargs)

    @property
    def diagnosis(self):
        return decrypt_string(self.diagnosis_encrypted)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"