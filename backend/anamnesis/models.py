
from django.db import models
from patients.models import Patient
from dictionaries.models import (
    ChronicDisease,
    HereditaryDisease,
    MedicationReference,
    AllergyReference,
)


class Anamnesis(models.Model):
    class StatusResponse(models.TextChoices):
        YES = "YES", "Да"
        NO = "NO", "Нет"
        UNKNOWN = "UNKNOWN", "Неизвестно"
        NOT_APPLICABLE = "NA", "Не применимо"

    class SmokingStatus(models.TextChoices):
        NEVER = "never", "Не курит"
        FORMER = "former", "Курил ранее"
        CURRENT = "current", "Курит"

    class AlcoholStatus(models.TextChoices):
        NEVER = "never", "Не употребляет"
        SOMETIMES = "sometimes", "Иногда"
        REGULARLY = "regularly", "Регулярно"

    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="anamnesis",
    )

    # Операции и госпитализации за последний год
    recent_events_notes = models.TextField(
        blank=True,
        default="",
    )

    pregnancy = models.CharField(
        max_length=10,
        choices=StatusResponse.choices,
        default=StatusResponse.UNKNOWN,
    )

    lactation = models.CharField(
        max_length=10,
        choices=StatusResponse.choices,
        default=StatusResponse.UNKNOWN,
    )

    smoking_status = models.CharField(
        max_length=20,
        choices=SmokingStatus.choices,
        null=True,
        blank=True,
    )

    alcohol_status = models.CharField(
        max_length=20,
        choices=AlcoholStatus.choices,
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(auto_now=True)


class PatientMedication(models.Model):
    class IntakeMode(models.TextChoices):
        CONSTANT = "CONSTANT", "Постоянно"
        AS_NEEDED = "AS_NEEDED", "По необходимости"

    anamnesis = models.ForeignKey(
        Anamnesis,
        on_delete=models.CASCADE,
        related_name="medications",
    )

    medication = models.ForeignKey(
        MedicationReference,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    custom_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )

    intake_mode = models.CharField(
        max_length=20,
        choices=IntakeMode.choices,
        default=IntakeMode.AS_NEEDED,
    )


class PatientAllergy(models.Model):
    anamnesis = models.ForeignKey(
        Anamnesis,
        on_delete=models.CASCADE,
        related_name="allergies",
    )

    allergen = models.ForeignKey(
        AllergyReference,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    custom_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )


class HereditaryDiseasePatient(models.Model):
    anamnesis = models.ForeignKey(
        Anamnesis,
        on_delete=models.CASCADE,
        related_name="hereditary_diseases",
    )

    disease = models.ForeignKey(
        HereditaryDisease,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    custom_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )


class PatientChronicDisease(models.Model):
    anamnesis = models.ForeignKey(
        Anamnesis,
        on_delete=models.CASCADE,
        related_name="chronic_diseases",
    )

    disease = models.ForeignKey(
        ChronicDisease,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    custom_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )
