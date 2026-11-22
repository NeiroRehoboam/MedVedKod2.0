import base64
import binascii
import secrets

from cryptography.exceptions import InvalidTag
from django.conf import settings
from rest_framework.exceptions import PermissionDenied

from consultations.crypto_module import (
    decrypt_data,
    derive_key_from_secret,
    encrypt_data,
    get_encryption_key,
    generate_salt,
)

SESSION_KEY_FIELD = 'medvedkod_personal_key'
DENIED_MESSAGE = 'Для работы с персональными данными войдите через MAX'


def _pepper() -> str:
    return getattr(settings, 'PERSONAL_DATA_PEPPER', '') or settings.SECRET_KEY


def _derive_kek(salt: bytes, user) -> bytes:
    return derive_key_from_secret(user.max_id, salt, _pepper())


def _session_dek(request, user=None) -> bytes | None:
    entry = request.session.get(SESSION_KEY_FIELD)
    user_id = user.pk if user is not None else getattr(request.user, 'pk', None)
    if not isinstance(entry, dict) or entry.get('user_id') != user_id:
        return None
    try:
        wrapped = base64.b64decode(entry['value'], validate=True)
        encoded = decrypt_data(get_encryption_key(), wrapped).decode('utf-8')
        dek = base64.b64decode(encoded, validate=True)
    except (InvalidTag, ValueError, TypeError, KeyError, binascii.Error, UnicodeDecodeError):
        return None
    return dek if len(dek) == 32 else None


def _store_dek(request, user, dek: bytes) -> None:
    encoded = base64.b64encode(dek).decode('ascii')
    wrapped = encrypt_data(get_encryption_key(), encoded.encode('utf-8'))
    request.session[SESSION_KEY_FIELD] = {
        'user_id': user.pk,
        'value': base64.b64encode(wrapped).decode('ascii'),
    }


def get_personal_key(request) -> bytes:
    dek = _session_dek(request)
    if dek is None:
        raise PermissionDenied(DENIED_MESSAGE)
    return dek


def clear_personal_key(request) -> None:
    request.session.pop(SESSION_KEY_FIELD, None)


def activate_personal_key(request, user, max_token: str) -> bytes:
    if not isinstance(max_token, str) or not max_token:
        raise PermissionDenied(DENIED_MESSAGE)

    if not user.has_personal_key:
        salt = generate_salt()
        dek = secrets.token_bytes(32)
        user.personal_salt = salt
        user.personal_key_encrypted = encrypt_data(_derive_kek(salt, user), dek)
        user.personal_key_version = 1
        user.save(update_fields=[
            'personal_salt',
            'personal_key_encrypted',
            'personal_key_version',
        ])
        _store_dek(request, user, dek)
        return dek

    salt = bytes(user.personal_salt)
    wrapped = bytes(user.personal_key_encrypted)
    try:
        dek = decrypt_data(_derive_kek(salt, user), wrapped)
    except (InvalidTag, ValueError):
        dek = _session_dek(request, user)
        if dek is None:
            raise PermissionDenied(DENIED_MESSAGE)
        user.personal_key_encrypted = encrypt_data(_derive_kek(salt, user), dek)
        user.personal_key_version = user.personal_key_version + 1
        user.save(update_fields=['personal_key_encrypted', 'personal_key_version'])

    if len(dek) != 32:
        raise PermissionDenied(DENIED_MESSAGE)

    _store_dek(request, user, dek)
    return dek
