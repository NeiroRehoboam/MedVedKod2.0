from django.db import models
from patients.models import Patient

class Anamnesis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='anamneses', verbose_name="Пациент")
    description = models.TextField(verbose_name="Описание анамнеза")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Анамнез #{self.id} — {self.patient}"