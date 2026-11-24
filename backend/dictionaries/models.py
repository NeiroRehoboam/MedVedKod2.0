from django.db import models


class AllergyType(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class HereditaryDisease(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class Specialty(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class AllergyReference(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class MedicationReference(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name


class ChronicDisease(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class PaymentType(models.Model):
    """Приоритетный вариант оплаты пациента (ОМС, ДМС, Платно)."""

    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
