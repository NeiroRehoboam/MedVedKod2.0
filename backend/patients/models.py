import uuid
from django.db import models

class TipAllergii(models.TextChoices):
    LEKARSTVENNAYA = "Лекарственная", "Лекарственная"
    PISHCHEVAYA = "Пищевая", "Пищевая"

class SpravochnikAllergenov(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nazvanie = models.CharField(max_length=200, blank=True, null=True)
    tip = models.CharField(max_length=50, choices=TipAllergii.choices, blank=True, null=True)
    aktivno = models.BooleanField(default=True)

    class Meta:
        db_table = "spravochnik_allergenov"
        managed = False

class SpravochnikLekarstv(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nazvanie = models.CharField(max_length=200, blank=True, null=True)
    aktivno = models.BooleanField(default=True)

    class Meta:
        db_table = "spravochnik_lekarstv"
        managed = False

class SpravochnikSpecialistov(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nazvanie = models.CharField(max_length=150, blank=True, null=True)
    aktivno = models.BooleanField(default=True)

    class Meta:
        db_table = "spravochnik_specialistov"
        managed = False

class SpravochnikZabolevaniy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nazvanie = models.CharField(max_length=200, blank=True, null=True)
    aktivno = models.BooleanField(default=True)

    class Meta:
        db_table = "spravochnik_zabolevaniy"
        managed = False

class Patsienty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    max_id = models.CharField(max_length=64, blank=True, null=True)
    data_registratsii = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patsienty"
        managed = False