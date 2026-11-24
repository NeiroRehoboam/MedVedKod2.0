
from django.db import models
from consultations.crypto_module import decrypt_field, encrypt_field
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
    recent_events_notes_encrypted = models.TextField(
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

    @property
    def _encryption_identity(self):
        return f'patient:{self.patient_id}'

    @property
    def recent_events_notes(self):
        return decrypt_field(self.recent_events_notes_encrypted, self._encryption_identity)

    @recent_events_notes.setter
    def recent_events_notes(self, value):
        self.recent_events_notes_encrypted = encrypt_field(value, self._encryption_identity)


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

    custom_name_encrypted = models.CharField(
        max_length=512,
        blank=True,
        default="",
    )

    @property
    def custom_name(self):
        return decrypt_field(self.custom_name_encrypted, f'patient:{self.anamnesis.patient_id}')

    @custom_name.setter
    def custom_name(self, value):
        self.custom_name_encrypted = encrypt_field(value, f'patient:{self.anamnesis.patient_id}')

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

    custom_name_encrypted = models.CharField(
        max_length=512,
        blank=True,
        default="",
    )

    @property
    def custom_name(self):
        return decrypt_field(self.custom_name_encrypted, f'patient:{self.anamnesis.patient_id}')

    @custom_name.setter
    def custom_name(self, value):
        self.custom_name_encrypted = encrypt_field(value, f'patient:{self.anamnesis.patient_id}')


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

    custom_name_encrypted = models.CharField(
        max_length=512,
        blank=True,
        default="",
    )

    @property
    def custom_name(self):
        return decrypt_field(self.custom_name_encrypted, f'patient:{self.anamnesis.patient_id}')

    @custom_name.setter
    def custom_name(self, value):
        self.custom_name_encrypted = encrypt_field(value, f'patient:{self.anamnesis.patient_id}')


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

    custom_name_encrypted = models.CharField(
        max_length=512,
        blank=True,
        default="",
    )

    @property
    def custom_name(self):
        return decrypt_field(self.custom_name_encrypted, f'patient:{self.anamnesis.patient_id}')

    @custom_name.setter
    def custom_name(self, value):
        self.custom_name_encrypted = encrypt_field(value, f'patient:{self.anamnesis.patient_id}')
