from rest_framework import serializers
from .models import RoutingResult

class RoutingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingResult
        fields = '__all__'