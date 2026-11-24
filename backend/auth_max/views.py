from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout, get_user_model
from drf_spectacular.utils import extend_schema
from .core_client import get_user_by_token
from .serializers import MaxLoginRequestSerializer, UserProfileSerializer
from patients.models import Patient

User = get_user_model()

# вход по токену MAX
@extend_schema(tags=['Auth'], request=MaxLoginRequestSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def max_login(request):
    user_jwt = request.data.get('token')
    if not user_jwt: return Response({'error': 'Токен не передан'}, status=400)
    try: profile = get_user_by_token(user_jwt)
    except Exception as e: return Response({'error': str(e)}, status=401)
    max_id = profile.get('_id'); full_name = profile.get('full_name', {})
    # пользователь и карта пациента
    user, created = User.objects.get_or_create(max_id=max_id, defaults={'first_name': full_name.get('firstName', ''), 'last_name': full_name.get('lastName', '')})
    Patient.objects.get_or_create(user=user)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return Response({'status': 'ok', 'user': {'id': user.id, 'max_id': user.max_id}})

# выход
@extend_schema(tags=['Auth'], request=None)
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response({'status': 'ok'})

# текущий пользователь
@extend_schema(tags=['Auth'], responses={200: UserProfileSerializer})
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request): return Response(UserProfileSerializer(request.user).data)