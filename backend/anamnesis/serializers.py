from django.db import transaction
from rest_framework import serializers
from .models import (
    Anamnesis, MedicalEvent, HereditaryDiseasePatient, 
    PatientMedication, PatientAllergy
)

# 1. Сериализаторы для дочерних таблиц
class MedicalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalEvent
        fields = ['id', 'event_type', 'description', 'event_date']

class HereditaryDiseasePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = HereditaryDiseasePatient
        fields = ['id', 'disease']

class PatientMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientMedication
        fields = ['id', 'medication', 'custom_name', 'intake_mode']

class PatientAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientAllergy
        fields = ['id', 'allergen', 'custom_name', 'allergy_type']


# 2. ГЛАВНЫЙ Сериализатор для всего Анамнеза
class FullAnamnesisSerializer(serializers.ModelSerializer):
    # Вкладываем дочерние сериализаторы. many=True означает, что это список
    medical_events = MedicalEventSerializer(many=True, required=False)
    hereditary_diseases = HereditaryDiseasePatientSerializer(many=True, required=False)
    medications = PatientMedicationSerializer(many=True, required=False)
    allergies = PatientAllergySerializer(many=True, required=False)

    class Meta:
        model = Anamnesis
        fields = [
            'id', 'smoking_status', 'alcohol_status', 'pregnancy', 'lactation',
            'medical_events', 'hereditary_diseases', 'medications', 'allergies'
        ]

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        patient = request.user.patient

        # Извлекаем вложенные данные
        medical_events_data = validated_data.pop('medical_events', [])
        hereditary_diseases_data = validated_data.pop('hereditary_diseases', [])
        medications_data = validated_data.pop('medications', [])
        allergies_data = validated_data.pop('allergies', [])

        # Создаем основной анамнез
        anamnesis = Anamnesis.objects.create(patient=patient, **validated_data)

        for event in medical_events_data:
            MedicalEvent.objects.create(anamnesis=anamnesis, **event)
            
        for disease in hereditary_diseases_data:
            HereditaryDiseasePatient.objects.create(anamnesis=anamnesis, **disease)
            
        for med in medications_data:
            PatientMedication.objects.create(anamnesis=anamnesis, **med)
            
        for allergy in allergies_data:
            PatientAllergy.objects.create(anamnesis=anamnesis, **allergy)

        return anamnesis