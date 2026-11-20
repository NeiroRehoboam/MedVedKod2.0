from rest_framework import serializers
from .models import Anamnesis

class AnamnesisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anamnesis
        fields = ['id', 'patient', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']