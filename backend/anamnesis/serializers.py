from django.db import transaction
from rest_framework import serializers
from .models import Anamnesis, MedicalEvent, HereditaryDiseasePatient, PatientMedication, PatientAllergy

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

class FullAnamnesisSerializer(serializers.ModelSerializer):
    medical_events = MedicalEventSerializer(many=True, required=False)
    hereditary_diseases = HereditaryDiseasePatientSerializer(many=True, required=False)
    medications = PatientMedicationSerializer(many=True, required=False)
    allergies = PatientAllergySerializer(many=True, required=False)

    class Meta:
        model = Anamnesis
        fields = ['id', 'smoking_status', 'alcohol_status', 'pregnancy', 'lactation', 'medical_events', 'hereditary_diseases', 'medications', 'allergies']

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        try:
            patient = request.user.patient
        except Exception:
            raise serializers.ValidationError("У пользователя нет карты пациента")

        events_data = validated_data.pop('medical_events', [])
        diseases_data = validated_data.pop('hereditary_diseases', [])
        meds_data = validated_data.pop('medications', [])
        allergies_data = validated_data.pop('allergies', [])

        anamnesis, created = Anamnesis.objects.update_or_create(patient=patient, defaults=validated_data)

        if not created:
            anamnesis.medical_events.all().delete()
            anamnesis.hereditary_diseases.all().delete()
            anamnesis.medications.all().delete()
            anamnesis.allergies.all().delete()

        for e in events_data: MedicalEvent.objects.create(anamnesis=anamnesis, **e)
        for d in diseases_data: HereditaryDiseasePatient.objects.create(anamnesis=anamnesis, **d)
        for m in meds_data: PatientMedication.objects.create(anamnesis=anamnesis, **m)
        for a in allergies_data: PatientAllergy.objects.create(anamnesis=anamnesis, **a)

        return anamnesis