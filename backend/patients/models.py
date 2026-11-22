import base64
import binascii

from cryptography.exceptions import InvalidTag
from django.conf import settings
from django.db import models

from consultations.crypto_module import decrypt_data, encrypt_data, get_encryption_key


def _decode_ciphertext(value: str) -> bytes:
    return base64.b64decode(value, validate=True)


def _decrypt(ciphertext: bytes, key: bytes) -> str:
    return decrypt_data(key, ciphertext).decode('utf-8')


class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='patient', 
        null=True, 
        blank=True
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    diagnosis_encrypted = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)

    def set_diagnosis(self, value: str, key: bytes) -> None:
        if not isinstance(value, str):
            raise TypeError('diagnosis must be str')
        if not isinstance(key, (bytes, bytearray)) or len(key) != 32:
            raise ValueError('key must be 32 bytes')
        if not value:
            self.diagnosis_encrypted = ''
            return
        encrypted = encrypt_data(bytes(key), value.encode('utf-8'))
        self.diagnosis_encrypted = base64.b64encode(encrypted).decode('ascii')

    def get_diagnosis(self, key: bytes) -> str:
        if not self.diagnosis_encrypted:
            return ''
        if not isinstance(key, (bytes, bytearray)) or len(key) != 32:
            raise ValueError('key must be 32 bytes')
        try:
            ciphertext = _decode_ciphertext(self.diagnosis_encrypted)
        except (binascii.Error, ValueError) as exc:
            raise ValueError('Encrypted diagnosis has invalid format') from exc

        try:
            return _decrypt(ciphertext, bytes(key))
        except (InvalidTag, ValueError, UnicodeDecodeError):
            try:
                return _decrypt(ciphertext, get_encryption_key())
            except (InvalidTag, ValueError, UnicodeDecodeError) as exc:
                raise ValueError('Unable to decrypt diagnosis') from exc

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
