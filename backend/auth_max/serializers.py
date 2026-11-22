from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class MaxLoginRequestSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="JWT из MAX")

class UserProfileSerializer(serializers.ModelSerializer):
    has_patient = serializers.SerializerMethodField()
    has_personal_key = serializers.BooleanField(read_only=True)
    personal_key_version = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'max_id', 'first_name', 'last_name',
            'is_staff', 'is_superuser', 'has_patient',
            'has_personal_key', 'personal_key_version'
        ]
        read_only_fields = fields

    def get_has_patient(self, obj):
        return hasattr(obj, 'patient') and obj.patient is not None