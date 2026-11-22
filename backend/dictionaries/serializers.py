from rest_framework import serializers
from .models import *

class BaseReferenceSerializer(serializers.ModelSerializer):
    class Meta: fields = ['id', 'name']

class SmokingStatusSerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = SmokingStatus

class AlcoholStatusSerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = AlcoholStatus

class AllergyTypeSerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = AllergyType

class MedicalEventTypeSerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = MedicalEventType

class HereditaryDiseaseSerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = HereditaryDisease

class SpecialtySerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = Specialty

class AllergyReferenceSerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = AllergyReference

class MedicationReferenceSerializer(BaseReferenceSerializer):
    class Meta(BaseReferenceSerializer.Meta): model = MedicationReference

class ComplaintCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintCategory
        fields = ['id', 'name', 'code']