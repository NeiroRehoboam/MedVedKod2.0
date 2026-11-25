from rest_framework import serializers

from dictionaries.models import PaymentType
from dictionaries.serializers import PaymentTypeSerializer
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    diagnosis = serializers.CharField(write_only=True, required=False)
    preferred_payment_detail = PaymentTypeSerializer(source='preferred_payment', read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'birth_date', 'diagnosis',
            'preferred_payment', 'preferred_payment_detail',
        ]


class PreferredPaymentUpdateSerializer(serializers.Serializer):
    """Приоритетная оплата пациента: только активные справочники или null."""

    preferred_payment = serializers.PrimaryKeyRelatedField(
        queryset=PaymentType.objects.filter(active=True),
        allow_null=True,
        required=True,
    )
