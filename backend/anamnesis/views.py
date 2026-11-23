
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import Anamnesis
from .serializers import FullAnamnesisSerializer


@extend_schema(
    tags=["Anamnesis"],
    request=FullAnamnesisSerializer,
    responses={200: FullAnamnesisSerializer, 201: FullAnamnesisSerializer},
)
class AnamnesisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        patient = getattr(request.user, "patient", None)

        if patient is None:
            return Response(
                {"error": "Карта пациента не найдена"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        anamnesis = Anamnesis.objects.filter(patient=patient).first()

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
