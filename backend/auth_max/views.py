from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout, get_user_model
from .core_client import get_user_by_token
from patients.models import Patient

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def max_login(request):
    user_jwt = request.data.get('token')
    if not user_jwt:
        return Response({'error': 'Токен не передан'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        profile = get_user_by_token(user_jwt)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    max_id = profile.get('_id')
    full_name = profile.get('full_name', {})
    
    user, created = User.objects.get_or_create(
        max_id=max_id,
        defaults={'first_name': full_name.get('firstName', ''), 'last_name': full_name.get('lastName', '')}
    )
    
    Patient.objects.get_or_create(user=user)
    
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return Response({'status': 'ok', 'user': {'id': user.id, 'max_id': user.max_id}})

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response({'status': 'ok'})