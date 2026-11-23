from django.contrib import admin
from .models import Anamnesis, HereditaryDiseasePatient, PatientMedication, PatientAllergy


class HereditaryDiseaseInline(admin.TabularInline):
    model = HereditaryDiseasePatient
    extra = 1


class PatientMedicationInline(admin.TabularInline):
    model = PatientMedication
    extra = 1


class PatientAllergyInline(admin.TabularInline):
    model = PatientAllergy
    extra = 1


@admin.register(Anamnesis)
class AnamnesisAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'smoking_status',
                    'alcohol_status', 'updated_at')
    inlines = [HereditaryDiseaseInline,
               PatientMedicationInline, PatientAllergyInline]
