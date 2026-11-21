import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model, login
from .core_client import get_user_by_token

User = get_user_model()

@csrf_exempt
@require_POST
def max_login(request):
    try:
        body = json.loads(request.body)
        user_jwt = body.get('token')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)

    if not user_jwt:
        return JsonResponse({'error': 'Токен не передан'}, status=400)

    try:
        profile = get_user_by_token(user_jwt)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=401)
    except PermissionError as e:
        return JsonResponse({'error': str(e)}, status=403)
    except LookupError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Ошибка Core: {e}'}, status=502)

    max_id = profile.get('_id')
    if not max_id:
        return JsonResponse({'error': 'Core не вернул _id'}, status=502)

    full_name = profile.get('full_name', {})
    user, created = User.objects.get_or_create(
        username=max_id,
        defaults={
            'first_name': full_name.get('firstName', ''),
            'last_name': full_name.get('lastName', ''),
        },
    )
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return JsonResponse({
        'status': 'ok',
        'user': {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    })