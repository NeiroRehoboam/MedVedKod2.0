from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'birth_date', 'user')
    search_fields = ('last_name', 'first_name')