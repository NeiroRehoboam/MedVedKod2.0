from django.conf import settings
from django.contrib.auth import get_user_model, login
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserProfileSerializer
from patients.models import Patient

User = get_user_model()


@extend_schema(
    exclude=True,
    tags=["Auth"],
    request=None,
    responses={200: UserProfileSerializer},
    description="Авторизация разработчика. Только для локальной разработки.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def demo_login(request):
    if not (settings.DEBUG and settings.ENABLE_DEMO_LOGIN):
        return Response(
            {"error": "Авторизация разработчика недоступна"},
            status=status.HTTP_403_FORBIDDEN,
        )

    demo_max_id = "medved-dev-user"

    user, created = User.objects.get_or_create(
        max_id=demo_max_id,
        defaults={
            "first_name": "Тестовый",
            "last_name": "Пациент",
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        },
    )

    if (
        not user.is_active
        or user.is_staff
        or user.is_superuser
        or user.groups.exists()
        or user.user_permissions.exists()
    ):
        return Response(
            {"error": "Недопустимые права тестового пользователя"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])

    Patient.objects.get_or_create(user=user)

    login(
        request,
        user,
        backend="django.contrib.auth.backends.ModelBackend",
    )

    return Response(UserProfileSerializer(user).data)
