from django.db import models
from patients.models import Patient

class Routing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='routings', verbose_name="Пациент")
    destination = models.CharField(max_length=200, verbose_name="Направление")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Маршрут #{self.id} — {self.patient} → {self.destination}"