from django.db import models
from patients.models import Patient
from dictionaries.models import (
    SmokingStatus, AlcoholStatus, MedicalEventType, 
    HereditaryDisease, MedicationReference, AllergyReference
)

class Anamnesis(models.Model):
    class StatusResponse(models.TextChoices):
        YES = 'YES', 'Да'
        NO = 'NO', 'Нет'
        UNKNOWN = 'UNKNOWN', 'Неизвестно'
        NOT_APPLICABLE = 'NA', 'Не применимо'

    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='anamnesis')
    smoking_status = models.ForeignKey(SmokingStatus, on_delete=models.SET_NULL, null=True, blank=True)
    alcohol_status = models.ForeignKey(AlcoholStatus, on_delete=models.SET_NULL, null=True, blank=True)
    pregnancy = models.CharField(max_length=20, choices=StatusResponse.choices, default=StatusResponse.NOT_APPLICABLE)
    lactation = models.CharField(max_length=20, choices=StatusResponse.choices, default=StatusResponse.NOT_APPLICABLE)
    updated_at = models.DateTimeField(auto_now=True)

class MedicalEvent(models.Model):
    anamnesis = models.ForeignKey(Anamnesis, on_delete=models.CASCADE, related_name='medical_events')
    event_type = models.ForeignKey(MedicalEventType, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    event_date = models.DateField(null=True, blank=True)

class HereditaryDiseasePatient(models.Model):
    anamnesis = models.ForeignKey(Anamnesis, on_delete=models.CASCADE, related_name='hereditary_diseases')
    disease = models.ForeignKey(HereditaryDisease, on_delete=models.PROTECT)

class PatientMedication(models.Model):
    class IntakeMode(models.TextChoices):
        CONSTANT = 'CONSTANT', 'Постоянно'
        AS_NEEDED = 'AS_NEEDED', 'По необходимости'

    anamnesis = models.ForeignKey(Anamnesis, on_delete=models.CASCADE, related_name='medications')
    medication = models.ForeignKey(MedicationReference, on_delete=models.PROTECT, null=True, blank=True)
    custom_name = models.CharField(max_length=200, blank=True, null=True)
    intake_mode = models.CharField(max_length=20, choices=IntakeMode.choices, default=IntakeMode.AS_NEEDED)

class PatientAllergy(models.Model):
    anamnesis = models.ForeignKey(Anamnesis, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.ForeignKey(AllergyReference, on_delete=models.PROTECT, null=True, blank=True)
    custom_name = models.CharField(max_length=200, blank=True, null=True)
    allergy_type = models.ForeignKey('dictionaries.AllergyType', on_delete=models.PROTECT)