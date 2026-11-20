from rest_framework import serializers
from .models import Routing

class RoutingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routing
        fields = ['id', 'patient', 'destination', 'created_at']
        read_only_fields = ['id', 'created_at']