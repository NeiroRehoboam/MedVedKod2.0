from django.db import models

class SmokingStatus(models.Model):
    name = models.CharField(max_length=50); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class AlcoholStatus(models.Model):
    name = models.CharField(max_length=50); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class AllergyType(models.Model):
    name = models.CharField(max_length=50); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class MedicalEventType(models.Model):
    name = models.CharField(max_length=50); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class HereditaryDisease(models.Model):
    name = models.CharField(max_length=100); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Specialty(models.Model):
    name = models.CharField(max_length=100); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class AllergyReference(models.Model):
    name = models.CharField(max_length=100); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class MedicationReference(models.Model):
    name = models.CharField(max_length=100); active = models.BooleanField(default=True)
    def __str__(self): return self.name

class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100); code = models.CharField(max_length=50, unique=True); active = models.BooleanField(default=True)
    def __str__(self): return self.name