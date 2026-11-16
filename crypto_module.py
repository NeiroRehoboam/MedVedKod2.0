import secrets
import random
from argon2 import PasswordHasher #требует установки
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM #требует установки
from argon2.low_level import hash_secret_raw, Type

def derive_key(password: str, salt: bytes) -> bytes:
    key = hash_secret_raw(
        secret=password.encode('utf-8'),
        salt=salt,  # ← исправлено: было salt_bytes
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
    except VerifyMismatchError: #InvalidHashError обрабатывается снаружи 
        return False

#AES-GCM новый стандарт для новго железа 

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

