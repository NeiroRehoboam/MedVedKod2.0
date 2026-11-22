from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    has_patient = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'max_id', 'first_name', 'last_name', 
            'is_staff', 'is_superuser', 'has_patient'
        ]
        read_only_fields = fields

    def get_has_patient(self, obj):
        return hasattr(obj, 'patient') and obj.patient is not None