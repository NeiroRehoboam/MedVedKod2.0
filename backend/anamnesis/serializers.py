
from django.db import transaction
from rest_framework import serializers

from .models import (
    Anamnesis,
    PatientChronicDisease,
    HereditaryDiseasePatient,
    PatientMedication,
    PatientAllergy,
)


class PatientChronicDiseaseSerializer(serializers.ModelSerializer):
    custom_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PatientChronicDisease
        fields = ["id", "disease", "custom_name"]
        read_only_fields = ["id"]


class HereditaryDiseasePatientSerializer(serializers.ModelSerializer):
    custom_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = HereditaryDiseasePatient
        fields = ["id", "disease", "custom_name"]
        read_only_fields = ["id"]


class PatientMedicationSerializer(serializers.ModelSerializer):
    custom_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PatientMedication
        fields = [
            "id",
            "medication",
            "custom_name",
            "intake_mode",
        ]
        read_only_fields = ["id"]


class PatientAllergySerializer(serializers.ModelSerializer):
    custom_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PatientAllergy
        fields = [
            "id",
            "allergen",
            "custom_name",
        ]
        read_only_fields = ["id"]


class FullAnamnesisSerializer(serializers.ModelSerializer):
    recent_events_notes = serializers.CharField(required=False, allow_blank=True)

    chronic_diseases = PatientChronicDiseaseSerializer(
        many=True,
        required=False,
    )

    hereditary_diseases = HereditaryDiseasePatientSerializer(
        many=True,
        required=False,
    )

    medications = PatientMedicationSerializer(
        many=True,
        required=False,
    )

    allergies = PatientAllergySerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Anamnesis
        fields = [
            "id",
            "smoking_status",
            "alcohol_status",
            "pregnancy",
            "lactation",
            "recent_events_notes",
            "chronic_diseases",
            "hereditary_diseases",
            "medications",
            "allergies",
        ]

        read_only_fields = ["id"]

    def _extract_nested(self, validated_data):
        nested = {}

        for field in (
            "chronic_diseases",
            "hereditary_diseases",
            "medications",
            "allergies",
        ):
            if field in validated_data:
                nested[field] = validated_data.pop(field)

        return nested

    def _save_nested(self, anamnesis, nested):
        models = {
            "chronic_diseases": PatientChronicDisease,
            "hereditary_diseases": HereditaryDiseasePatient,
            "medications": PatientMedication,
            "allergies": PatientAllergy,
        }

        for field, items in nested.items():
            relation = getattr(anamnesis, field)

            # Заменяем записи только переданного раздела.
            relation.all().delete()

            models[field].objects.bulk_create(
                [
                    models[field](
                        anamnesis=anamnesis,
                        **item,
                    )
                    for item in items
                ]
            )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]

        try:
            patient = request.user.patient
        except AttributeError:
            raise serializers.ValidationError(
                "У пользователя нет карты пациента"
            )

        nested = self._extract_nested(validated_data)

        anamnesis, _ = Anamnesis.objects.update_or_create(
            patient=patient,
            defaults=validated_data,
        )

        self._save_nested(anamnesis, nested)

        return anamnesis

    @transaction.atomic
    def update(self, instance, validated_data):
        nested = self._extract_nested(validated_data)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        self._save_nested(instance, nested)

        return instance
