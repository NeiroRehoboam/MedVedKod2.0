from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from auth_max.key_management import get_personal_key
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    diagnosis = serializers.CharField(write_only=True, required=False, allow_blank=True)
    diagnosis_value = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'diagnosis', 'diagnosis_value']

    def _key(self) -> bytes:
        request = self.context.get('request')
        if request is None:
            raise PermissionDenied('Для работы с персональными данными войдите через MAX')
        return get_personal_key(request)

    def get_diagnosis_value(self, obj):
        return obj.get_diagnosis(self._key())

    def create(self, validated_data):
        diagnosis = validated_data.pop('diagnosis', None)
        patient = Patient(**validated_data)
        if diagnosis is not None:
            patient.set_diagnosis(diagnosis, self._key())
        patient.save()
        return patient

    def update(self, instance, validated_data):
        diagnosis = validated_data.pop('diagnosis', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if diagnosis is not None:
            instance.set_diagnosis(diagnosis, self._key())
        instance.save()
        return instance
