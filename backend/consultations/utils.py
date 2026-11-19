import base64
from cryptography.fernet import Fernet
from django.conf import settings

def _fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    if isinstance(key, str):
        key = key.encode()
    return Fernet(base64.urlsafe_b64encode(key[:32].ljust(32, b"0")))

def encrypt_data(data: str | None) -> bytes | None:
    if not data:
        return None
    return _fernet().encrypt(data.encode("utf-8"))

def decrypt_data(data: bytes | None) -> str | None:
    if not data:
        return None
    return _fernet().decrypt(bytes(data)).decode("utf-8")