import os, requests
CORE_BASE_URL = os.getenv('CORE_BASE_URL', 'https://tm-test-yakut.hostco.ru')
CORE_SERVICE_TOKEN = os.getenv('CORE_SERVICE_TOKEN')

def get_user_by_token(user_jwt: str) -> dict:
    url = f"{CORE_BASE_URL}/api/v3/users/user-for-external-service"
    headers = {"Authorization": f"Bearer {CORE_SERVICE_TOKEN}"}
    params = {"token": user_jwt}
    # запрос профиля в MAX Core
    response = requests.get(url, headers=headers, params=params, timeout=10)

    # разбор ответа
    if response.status_code == 401: raise ValueError("JWT просрочен")
    if response.status_code == 403: raise PermissionError("Сервисный токен неверный")
    if response.status_code == 404: raise LookupError("Пользователь не найден")
    if not response.ok: raise RuntimeError(f"Core ответил {response.status_code}")
    return response.json()