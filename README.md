# MedVedKod2.0

## Установка бэкенда

1. Клонируйте репозиторий:
   ```bash
    git clone <url>
    cd MedVedKod2.0

2. Создайте виртуальное окружение  
    # Windows PowerShell
    cd backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1
3. Установите зависимости:
    pip install -r requirements.txt

4. Создайте файл .env на основе шаблона:
    cp .env.example .env
    # Отредактируйте .env, укажите пароль от PostgreSQL(если не указан)



6. Примените миграции:
    python manage.py migrate
    python manage.py runserver

7. Запустите сервер
    python manage.py runserver
