import base64
import secrets
import random

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from django.conf import settings


class DecryptionError(Exception):
    pass


class LegacyCiphertextError(DecryptionError):
    pass


VERSION = b'\x01'
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
INFO_PREFIX = b'patient.diagnosis.v1|'


def derive_key(password: str, salt: bytes) -> bytes:
    key = hash_secret_raw(
        secret=password.encode('utf-8'),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID
    )
    return key

LOWER="abcdefghijklmnopqrstuvwxyz"
UPPER="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS="0123456789"
SPECIAL="!#$%&()*+,-.;<=>?@[]^_`{|}~"
ALPHABET=LOWER+UPPER+DIGITS+SPECIAL

secure_random=random.SystemRandom()
ph=PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)

def generate_password(length: int) -> str:

    if length<8:
        raise ValueError("Password too short")
    if length>1028:
            raise ValueError("Password too long")

    chars=[]
    chars.append(secrets.choice(LOWER))
    chars.append(secrets.choice(UPPER))
    chars.append(secrets.choice(DIGITS))
    chars.append(secrets.choice(SPECIAL))

    for _ in range(length-4):
        chars.append(secrets.choice(ALPHABET))
    secure_random.shuffle(chars)
    return "".join(chars)

def generate_hash_argon2(password: str) -> str:
    if password is None or password=='':
        raise ValueError("Password too None or null")
    return ph.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        ph.verify(stored_hash, password)
        return True
    except VerifyMismatchError:
        return False

def encrypt_data(key: bytes, data: bytes) -> bytes:
    nonce=secrets.token_bytes(12)
    aesgcm=AESGCM(key)
    ciphertext=aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext

def decrypt_data(key: bytes, encrypted_data: bytes) -> bytes:
    nonce=encrypted_data[:12]
    ciphertext=encrypted_data[12:]
    aesgcm=AESGCM(key)
    plaintext=aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext


def _derive_encryption_key(salt: bytes, identity: str) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=INFO_PREFIX + identity.encode('utf-8'),
    ).derive(settings.ENCRYPTION_PEPPER.encode('utf-8'))


def encrypt_string(text: str, identity: str) -> str:
    if not text:
        return ''
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    key = _derive_encryption_key(salt, identity)
    ciphertext = AESGCM(key).encrypt(nonce, text.encode('utf-8'), identity.encode('utf-8'))
    return base64.b64encode(VERSION + salt + nonce + ciphertext).decode('utf-8')


def decrypt_string(encrypted_b64: str, identity: str) -> str:
    if not encrypted_b64:
        return ''
    try:
        raw = base64.b64decode(encrypted_b64, validate=True)
    except Exception as exc:
        raise DecryptionError('Некорректный формат зашифрованных данных') from exc
    min_size = 1 + SALT_SIZE + NONCE_SIZE + TAG_SIZE
    if len(raw) < min_size or raw[:1] != VERSION:
        raise LegacyCiphertextError('Значение зашифровано старым форматом')
    salt = raw[1:1 + SALT_SIZE]
    nonce = raw[1 + SALT_SIZE:1 + SALT_SIZE + NONCE_SIZE]
    ciphertext = raw[1 + SALT_SIZE + NONCE_SIZE:]
    key = _derive_encryption_key(salt, identity)
    try:
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, identity.encode('utf-8'))
        return plaintext.decode('utf-8')
    except Exception as exc:
        raise DecryptionError('Не удалось расшифровать данные') from exc


def encrypt_field(value, identity):
    return encrypt_string(value, identity) if value is not None else None


def decrypt_field(value, identity):
    return decrypt_string(value, identity) if value is not None else None
