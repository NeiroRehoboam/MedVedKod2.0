from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class MaxLoginRequestSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

class UserProfileSerializer(serializers.ModelSerializer):
    has_patient = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'max_id', 'first_name', 'last_name', 'is_staff', 'has_patient']
    def get_has_patient(self, obj):
        return hasattr(obj, 'patient') and obj.patient is not None