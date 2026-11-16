import uuid
from django.db import models
from patients.models import Patsienty, SpravochnikAllergenov, SpravochnikLekarstv, SpravochnikZabolevaniy

class StatusKureniya(models.TextChoices):
    NE_KURIT = "Не курит", "Не курит"
    KURIL_RANEE = "Курил ранее", "Курил ранее"
    KURIT = "Курит", "Курит"

class StatusAlkogolya(models.TextChoices):
    NE_UPOTREBLYAET = "Не употребляет", "Не употребляет"
    INOGDA = "Иногда", "Иногда"
    REGULYARNO = "Регулярно", "Регулярно"

class Nasledstvennost(models.TextChoices):
    SERDECHNO_SOSUDISTYE = "Сердечно-сосудистые заболевания", "Сердечно-сосудистые заболевания"
    ONKOLOGIYA = "Онкология", "Онкология"
    DIABET = "Диабет", "Диабет"

class RezhimPriema(models.TextChoices):
    POSTOYANNO = "Постоянно", "Постоянно"
    PO_NEOBHODIMOSTI = "По необходимости", "По необходимости"

class TipSobytiya(models.TextChoices):
    OPERATSIYA = "Операция", "Операция"
    GOSPITALIZATSIYA = "Госпитализация", "Госпитализация"

class Anamnez(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patsient = models.ForeignKey(Patsienty, on_delete=models.CASCADE, db_column="patsient")
    beremennost = models.BooleanField(blank=True, null=True)
    laktatsiya = models.BooleanField(blank=True, null=True)
    kurenie_status = models.CharField(max_length=50, choices=StatusKureniya.choices, blank=True, null=True)
    alkogol_status = models.CharField(max_length=50, choices=StatusAlkogolya.choices, blank=True, null=True)
    data_obnovleniya = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "anamnez"
        managed = False

class AllergiiPatsienta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anamnez = models.ForeignKey(Anamnez, on_delete=models.CASCADE, db_column="anamnez")
    allergen = models.ForeignKey(SpravochnikAllergenov, on_delete=models.SET_NULL, blank=True, null=True, db_column="allergen")
    svoy_variant = models.BinaryField(blank=True, null=True)
    tip_svoego_variants = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "allergii_patsienta"
        managed = False

class LekarstvaPatsienta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anamnez = models.ForeignKey(Anamnez, on_delete=models.CASCADE, db_column="anamnez")
    lekarstvo = models.ForeignKey(SpravochnikLekarstv, on_delete=models.SET_NULL, blank=True, null=True, db_column="lekarstvo")
    svoy_variant = models.BinaryField(blank=True, null=True)
    rezhim_priema = models.CharField(max_length=50, choices=RezhimPriema.choices, blank=True, null=True)

    class Meta:
        db_table = "lekarstva_patsienta"
        managed = False

class MeditsinskieSobytiya(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anamnez = models.ForeignKey(Anamnez, on_delete=models.CASCADE, db_column="anamnez")
    tip_sobytiya = models.CharField(max_length=50, choices=TipSobytiya.choices, blank=True, null=True)
    opisaniye = models.BinaryField(blank=True, null=True)
    data_sobytiya = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "meditsinskie_sobytiya"
        managed = False

class NasledstvennostPatsienta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anamnez = models.ForeignKey(Anamnez, on_delete=models.CASCADE, db_column="anamnez")
    zabolevanie = models.CharField(max_length=100, choices=Nasledstvennost.choices, blank=True, null=True)

    class Meta:
        db_table = "nasledstvennost_patsienta"
        managed = False

class ZabolevaniyaPatsienta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anamnez = models.ForeignKey(Anamnez, on_delete=models.CASCADE, db_column="anamnez")
    zabolevanie = models.ForeignKey(SpravochnikZabolevaniy, on_delete=models.SET_NULL, blank=True, null=True, db_column="zabolevanie")
    svoy_variant = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = "zabolevaniya_patsienta"
        managed = False