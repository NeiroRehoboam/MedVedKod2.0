from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.utils import timezone

from ..ai_assis.services import SessionService
from .models import VoprosySessii
from .utils import encrypt_data


class StartSessionSerializer(serializers.Serializer):
    max_id = serializers.CharField(max_length=64)
    session_name = serializers.CharField(max_length=255)


class AddQuestionSerializer(serializers.Serializer):
    sessiya_id = serializers.UUIDField()
    text = serializers.CharField()
    source = serializers.CharField(max_length=20, required=False, default="Система")
    order = serializers.IntegerField()
    answers = serializers.ListField(
        child=serializers.CharField(), 
        required=False, 
        allow_empty=True
    )


class AnswerSerializer(serializers.Serializer):
    vopros_id = serializers.UUIDField()
    answer = serializers.CharField()



class StartSessionView(APIView):
    """Создание новой сессии для пациента."""
    def post(self, request):
        serializer = StartSessionSerializer(data=request.data)
        if serializer.is_valid():
            sessiya = SessionService.start_session(
                patsient_max_id=serializer.validated_data["max_id"], 
                session_name=serializer.validated_data["session_name"]
            )
            return Response(
                {"sessiya_id": str(sessiya.id)}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddQuestionView(APIView):
    """Добавление вопроса в текущую сессию."""
    def post(self, request):
        serializer = AddQuestionSerializer(data=request.data)
        if serializer.is_valid():
            vopros = SessionService.add_question(
                sessiya_id=str(serializer.validated_data["sessiya_id"]),
                text=serializer.validated_data["text"],
                source=serializer.validated_data.get("source", "Система"),
                order=serializer.validated_data["order"],
                answers=serializer.validated_data.get("answers"),
            )
            return Response(
                {"vopros_id": str(vopros.id)}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnswerView(APIView):
    """Сохранение ответа пациента на вопрос."""
    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            vopros = VoprosySessii.objects.get(id=serializer.validated_data["vopros_id"])
            vopros.tekst_otveta = encrypt_data(serializer.validated_data["answer"])
            vopros.data_otveta = timezone.now()
            vopros.save(update_fields=["tekst_otveta", "data_otveta"])
            
            return Response({"status": "ok"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)