from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    diagnosis = serializers.CharField(source='diagnosis_encrypted', write_only=True, required=False)
    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'diagnosis']