from django.contrib import admin
from .models import Anamnesis, MedicalEvent, HereditaryDiseasePatient, PatientMedication, PatientAllergy

class MedicalEventInline(admin.TabularInline):
    model = MedicalEvent
    extra = 1

class PatientAllergyInline(admin.TabularInline):
    model = PatientAllergy
    extra = 1

@admin.register(Anamnesis)
class AnamnesisAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'smoking_status', 'alcohol_status', 'updated_at')
    inlines = [MedicalEventInline, PatientAllergyInline]