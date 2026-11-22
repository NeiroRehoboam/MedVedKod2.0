from rest_framework import serializers
from .models import RoutingResult
from dictionaries.serializers import SpecialtySerializer
from dictionaries.models import Specialty

class RoutingResultSerializer(serializers.ModelSerializer):
    # Для чтения (GET): возвращаем словарь с названием специальности
    specialty_detail = SpecialtySerializer(source='specialty', read_only=True)
    
    # Для записи (POST): принимаем ID специальности
    specialty = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects.all(), 
        required=False, 
        allow_null=True
    )

    class Meta:
        model = RoutingResult
        fields = [
            'id', 'session', 'urgency', 'specialty', 'specialty_detail', 
            'justification', 'recommendations', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']