from django.contrib import admin
from .models import (
    SmokingStatus, AllergyType, MedicalEventType, 
    HereditaryDisease, Specialty, AllergyReference, MedicationReference
)

@admin.register(SmokingStatus)
class SmokingStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')

@admin.register(AllergyType)
class AllergyTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')

@admin.register(MedicalEventType)
class MedicalEventTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')

@admin.register(HereditaryDisease)
class HereditaryDiseaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')

@admin.register(AllergyReference)
class AllergyReferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')

@admin.register(MedicationReference)
class MedicationReferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')