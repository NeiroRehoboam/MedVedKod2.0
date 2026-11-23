from django.contrib import admin
from .models import *

@admin.register(AllergyType)
class AllergyTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active'); list_editable = ('active',)

@admin.register(HereditaryDisease)
class HereditaryDiseaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active'); list_editable = ('active',)

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active'); list_editable = ('active',)

@admin.register(AllergyReference)
class AllergyReferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active'); list_editable = ('active',)

@admin.register(MedicationReference)
class MedicationReferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active'); list_editable = ('active',)

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'active'); list_editable = ('active',)