
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import Anamnesis
from .serializers import FullAnamnesisSerializer


@extend_schema(tags=["Anamnesis"])
class AnamnesisView(APIView):
    permission_classes = [IsAuthenticated]

    # чтение анамнеза
    @extend_schema(
        responses={200: FullAnamnesisSerializer},
    )
    def get(self, request):
        anamnesis = (
            Anamnesis.objects
            .filter(patient__user=request.user)
            .prefetch_related(
                "chronic_diseases",
                "hereditary_diseases",
                "allergies",
                "medications",
            )
            .first()
        )

        if anamnesis is None:
            return Response(
                {"detail": "Анамнез ещё не заполнен"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FullAnamnesisSerializer(anamnesis)
        return Response(serializer.data)

    # сохранение анамнеза
    @extend_schema(
        request=FullAnamnesisSerializer,
        responses={
            200: FullAnamnesisSerializer,
            201: FullAnamnesisSerializer,
        },
    )
    def post(self, request):
        patient = getattr(request.user, "patient", None)

        if patient is None:
            return Response(
                {"detail": "Карта пациента не найдена"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        anamnesis = Anamnesis.objects.filter(
            patient=patient
        ).first()

        serializer = FullAnamnesisSerializer(
            instance=anamnesis,
            data=request.data,
            partial=anamnesis is not None,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=(
                status.HTTP_200_OK
                if anamnesis
                else status.HTTP_201_CREATED
            ),
        )
