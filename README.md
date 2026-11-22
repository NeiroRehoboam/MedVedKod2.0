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


## crypto_module

Криптографический модуль для безопасной работы с паролями и шифрования данных. Реализует современные стандарты: Argon2id для хеширования, AES-256-GCM для шифрования.

### Установка зависимостей

```bash
pip install argon2-cffi cryptography
```

### Функции модуля

#### `generate_password(length: int) -> str`

Генерирует криптостойкий пароль длиной от 8 до 1028 символов.

- Алфавит: 89 символов (`a-z`, `A-Z`, `0-9`, ``!#$%&()*+,-.;<=>?@[]^_`{|}~``).
- Гарантирует наличие хотя бы одного символа из каждого класса.
- Использует `random.SystemRandom()` для криптостойкой случайности.
- Энтропия при длине 16: ~103.6 бит.
- Исключения: `ValueError` (длина вне диапазона 8-1028), `TypeError` (`length` не `int`).

Пример:

```python
pwd = generate_password(16)
# "Ri}8)tUj27EOg{-Y"
```

#### `generate_hash_argon2(password: str) -> str`

Хеширует пароль через Argon2id.

- Параметры: `memory_cost=65536` (64 MB), `time_cost=3`, `parallelism=4`.
- Автоматически генерирует уникальную соль (16 байт) и включает её в результат.
- Возвращает строку в PHC-формате: `$argon2id$v=19$m=65536,t=3,p=4$<salt_base64>$<hash_base64>`.
- Один и тот же пароль даёт разные хеши (защита от радужных таблиц).
- Исключения: `ValueError` (`password is None` или `password == ''`).

Пример:

```python
h = generate_hash_argon2("MyPass")
# "$argon2id$v=19$m=65536,t=3,p=4$fQin...$9LUj..."
```

#### `verify_password(password: str, stored_hash: str) -> bool`

Проверяет введённый пароль по сохранённому хешу.

- Автоматически извлекает соль и параметры из `stored_hash`.
- Возвращает `True`, если пароль правильный, и `False`, если неправильный.
- Исключения: `InvalidHashError` из `argon2.exceptions` (`stored_hash` повреждён или имеет неправильный формат; обрабатывается снаружи).

Пример:

```python
verify_password("MyPass", h)  # True или False
```

#### `encrypt_data(key: bytes, data: bytes) -> bytes`

Шифрует данные через AES-256-GCM (AEAD-режим).

- `key` должен быть 32 байта (256 бит).
- Автоматически генерирует уникальный nonce (12 байт) через `secrets.token_bytes(12)`.
- Возвращает байтовую строку формата: nonce (12 байт) + ciphertext + tag (16 байт).
- Тег аутентификации проверяет целостность: если данные повреждены или ключ неправильный, расшифровка упадёт с ошибкой.
- Исключения: `ValueError` (`key` не 32 байта), `TypeError` (`key` или `data` не `bytes`).

Пример:

```python
encrypted = encrypt_data(key, b"Secret data")
```

#### `decrypt_data(key: bytes, encrypted_data: bytes) -> bytes`

Расшифровывает данные, зашифрованные через `encrypt_data`.

- Автоматически извлекает nonce из первых 12 байт `encrypted_data`.
- Проверяет тег аутентификации.
- Возвращает исходные данные (`bytes`).
- Исключения: `InvalidTag` из `cryptography.exceptions` (ключ неправильный или данные повреждены), `ValueError` (`key` не 32 байта или `encrypted_data` слишком короткий), `TypeError` (`key` или `encrypted_data` не `bytes`).

Пример:

```python
decrypted = decrypt_data(key, encrypted)  # b"Secret data"
```

#### `derive_key(password: str, salt: bytes) -> bytes`

Получает 32-байтовый ключ AES-256 из пароля через Argon2id (KDF).

- `password` — строка, `salt` — 16 байт (генерируется через `secrets.token_bytes(16)`).
- Детерминированная функция: один пароль + одна соль = один и тот же ключ.
- Соль нужно хранить отдельно (в базе данных).
- Параметры Argon2: `memory_cost=65536`, `time_cost=3`, `parallelism=4`.
- Возвращает 32 байта ключа.
- Исключения: `ValueError` (`salt` не 16 байт), `TypeError` (`password` не `str` или `salt` не `bytes`).

Пример использования:

```python
salt = secrets.token_bytes(16)
key = derive_key("MyPass", salt)
encrypted = encrypt_data(key, b"Secret")

# Сохранить salt и encrypted в базу.

# Для расшифровки:
key_again = derive_key("MyPass", salt)
decrypted = decrypt_data(key_again, encrypted)
```

#### `generate_salt(size: int = 16) -> bytes`

Генерирует криптостойкую соль размером 16 байт через `secrets.token_bytes()`.

```python
salt = generate_salt()
```

#### `derive_key_from_secret(secret: str, salt: bytes, pepper: str = "") -> bytes`

Выводит 32-байтовый ключ из секрета пользователя, соли и серверного pepper через Argon2id (`memory_cost=65536`, `time_cost=3`, `parallelism=4`).

- `secret` — строка-пароль (например, `max_id`, полученный из профиля MAX).
- `salt` — 16 байт, уникальных для пользователя.
- `pepper` — серверный секрет из `PERSONAL_DATA_PEPPER` (по умолчанию `SECRET_KEY`).

```python
salt = generate_salt()
kek = derive_key_from_secret(user.max_id, salt, settings.PERSONAL_DATA_PEPPER)
```

### Хранение персональных данных

При входе через MAX (`POST /api/auth/max-login/`) `max_id` из профиля MAX используется как пароль пользователя; сам JWT не сохраняется:

1. Создаётся уникальная соль (`User.personal_salt`) и случайный 32-байтовый ключ данных.
2. Ключ данных шифруется ключом, выведенным из `max_id`, соли и `PERSONAL_DATA_PEPPER`, и сохраняется в `User.personal_key_encrypted`.
3. Расшифрованный ключ живёт только в серверной сессии (в зашифрованном виде) и удаляется при logout.
4. Персональные данные пациента шифруются этим ключом; старые значения, зашифрованные глобальным `SECRET_KEY`, всё ещё читаются.
5. Запросы с JWT, но без MAX-сессии, не получают доступ к персональным данным (403).

### Безопасность

- Минимальная длина пароля 8 символов (~97 бит энтропии).
- Для данных особой важности рекомендуется 20+ символов (~128 бит энтропии).
- Не используйте SHA-256 для паролей: он слишком быстрый.
- Не переиспользуйте nonce с одним ключом — это приведёт к компрометации.
- Соль для KDF храните отдельно от зашифрованных данных.
