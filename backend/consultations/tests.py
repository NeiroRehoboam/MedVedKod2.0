import base64

from django.contrib.auth import get_user_model
from django.test import TestCase

from consultations.crypto_module import (
    DecryptionError,
    LegacyCiphertextError,
    decrypt_string,
    encrypt_string,
)

User = get_user_model()


class CryptoModuleTests(TestCase):
    def test_encryption_is_randomized_and_roundtrips(self):
        first = encrypt_string('Головная боль', 'user:1')
        second = encrypt_string('Головная боль', 'user:1')
        self.assertNotEqual(first, second)
        self.assertEqual(decrypt_string(first, 'user:1'), 'Головная боль')
        self.assertEqual(decrypt_string(second, 'user:1'), 'Головная боль')

    def test_wrong_identity_fails(self):
        ciphertext = encrypt_string('секрет', 'user:1')
        with self.assertRaises(DecryptionError):
            decrypt_string(ciphertext, 'user:2')

    def test_wrong_pepper_fails(self):
        ciphertext = encrypt_string('секрет', 'user:1')
        with self.settings(ENCRYPTION_PEPPER='x' * 64):
            with self.assertRaises(DecryptionError):
                decrypt_string(ciphertext, 'user:1')

    def test_legacy_value_is_rejected(self):
        legacy = base64.b64encode(b'old-format-payload').decode('utf-8')
        with self.assertRaises(LegacyCiphertextError):
            decrypt_string(legacy, 'user:1')

    def test_empty_value(self):
        self.assertEqual(encrypt_string('', 'user:1'), '')
        self.assertEqual(decrypt_string('', 'user:1'), '')
