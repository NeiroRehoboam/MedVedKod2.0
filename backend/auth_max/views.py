from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import login, logout, get_user_model
from drf_spectacular.utils import extend_schema
from .core_client import get_user_by_token
from .key_management import activate_personal_key, clear_personal_key
from .serializers import UserProfileSerializer, MaxLoginRequestSerializer
from patients.models import Patient

User = get_user_model()

@extend_schema(tags=['Auth'], request=MaxLoginRequestSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def max_login(request):
    user_jwt = request.data.get('token')
    if not user_jwt:
        return Response({'error': 'Токен не передан'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = get_user_by_token(user_jwt)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except PermissionError as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except LookupError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({'error': 'Ошибка при обращении к Core'}, status=status.HTTP_502_BAD_GATEWAY)

    max_id = profile.get('_id')
    if not max_id:
        return Response({'error': 'Core не вернул _id'}, status=status.HTTP_502_BAD_GATEWAY)

    full_name = profile.get('full_name', {})

    user, created = User.objects.get_or_create(
        max_id=max_id,
        defaults={
            'first_name': full_name.get('firstName', ''),
            'last_name': full_name.get('lastName', ''),
        },
    )

    if not created:
        user.first_name = full_name.get('firstName', '')
        user.last_name = full_name.get('lastName', '')
        user.save()

    # Создаем карту пациента при первом входе
    Patient.objects.get_or_create(
        user=user,
        defaults={
            'first_name': full_name.get('firstName', ''),
            'last_name': full_name.get('lastName', ''),
            'birth_date': '1900-01-01',
        }
    )

    activate_personal_key(request, user, user_jwt)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return Response({'status': 'ok', 'user': {'id': user.id, 'max_id': user.max_id}})

    return Response({
        'status': 'ok',
        'user': {
            'id': user.id,
            'max_id': user.max_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
        'has_personal_key': user.has_personal_key,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    clear_personal_key(request)
    logout(request)
    return Response({'status': 'ok'})

@extend_schema(tags=['Auth'], responses={200: UserProfileSerializer})
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)