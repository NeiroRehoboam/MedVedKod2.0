import uuid
from django.db import models
from patients.models import Patsienty # Импортируем пациента

class IstochnikVoprosa(models.TextChoices):
    SISTEMA = "Система", "Система"
    II = "ИИ", "ИИ"

class StatusSessii(models.TextChoices):
    V_PROTSESSE = "В процессе", "В процессе"
    ZAVERSHENA = "Завершена", "Завершена"

class consultations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patsient = models.ForeignKey(Patsienty, on_delete=models.CASCADE, db_column="patsient")
    nazvanie = models.BinaryField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=StatusSessii.choices, blank=True, null=True)
    data_sozdaniya = models.DateTimeField(auto_now_add=True)
    data_obnovleniya = models.DateTimeField(auto_now=True)
    data_zaversheniya = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "sessii"
        managed = False

class VoprosySessii(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessiya = models.ForeignKey(consultations, on_delete=models.CASCADE, db_column="sessiya")
    tekst_voprosa = models.BinaryField(blank=True, null=True)
    tekst_otveta = models.BinaryField(blank=True, null=True)
    poryadkovyy_nomer = models.IntegerField(blank=True, null=True)
    istochnik = models.CharField(max_length=50, choices=IstochnikVoprosa.choices, blank=True, null=True)
    data_sozdaniya = models.DateTimeField(auto_now_add=True)
    data_otveta = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "voprosy_sessii"
        managed = False

class BystryeOtvety(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vopros = models.ForeignKey(VoprosySessii, on_delete=models.CASCADE, db_column="vopros")
    tekst = models.BinaryField(blank=True, null=True)
    poryadkovyy_nomer = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "bystrye_otvety"
        managed = False