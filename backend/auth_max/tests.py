from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from consultations.crypto_module import derive_key_from_secret
from patients.models import Patient

User = get_user_model()


@override_settings(PERSONAL_DATA_PEPPER='test-pepper')
class MaxLoginPersonalKeyTests(TestCase):
    def _profile(self, max_id='max-1'):
        return {
            '_id': max_id,
            'full_name': {'firstName': 'Иван', 'lastName': 'Иванов'},
        }

    @patch('auth_max.views.get_user_by_token')
    def test_login_creates_user_patient_and_personal_key(self, get_user):
        get_user.return_value = self._profile()

        response = self.client.post(
            reverse('max-login'),
            {'token': 'max-token-1'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(max_id='max-1')
        self.assertTrue(user.has_personal_key)
        self.assertEqual(len(bytes(user.personal_salt)), 16)
        self.assertEqual(len(bytes(user.personal_key_encrypted)), 60)
        self.assertTrue(Patient.objects.filter(user=user).exists())
        self.assertIn('medvedkod_personal_key', self.client.session)
        self.assertNotIn('max-token-1', response.content.decode())

    @patch('auth_max.views.get_user_by_token')
    def test_repeated_login_keeps_same_key(self, get_user):
        get_user.return_value = self._profile()
        url = reverse('max-login')

        self.client.post(url, {'token': 'max-token-1'}, content_type='application/json')
        user = User.objects.get(max_id='max-1')
        first_dek = derive_key_from_secret('max-1', bytes(user.personal_salt), 'test-pepper')

        response = self.client.post(url, {'token': 'max-token-2'}, content_type='application/json')
        user.refresh_from_db()
        second_dek = derive_key_from_secret('max-1', bytes(user.personal_salt), 'test-pepper')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_dek, second_dek)
        self.assertEqual(user.personal_key_version, 1)

    @patch('auth_max.views.get_user_by_token')
    def test_pepper_rotation_rewraps_key_using_session(self, get_user):
        get_user.return_value = self._profile()
        url = reverse('max-login')

        self.client.post(url, {'token': 'max-token-1'}, content_type='application/json')
        with override_settings(PERSONAL_DATA_PEPPER='new-pepper'):
            response = self.client.post(url, {'token': 'max-token-1'}, content_type='application/json')

        user = User.objects.get(max_id='max-1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.personal_key_version, 2)

    @patch('auth_max.views.get_user_by_token')
    def test_each_user_has_own_salt_and_key(self, get_user):
        url = reverse('max-login')

        for max_id in ('max-1', 'max-2'):
            get_user.return_value = self._profile(max_id)
            client = Client()
            response = client.post(url, {'token': f'token-{max_id}'}, content_type='application/json')
            self.assertEqual(response.status_code, 200)

        first = User.objects.get(max_id='max-1')
        second = User.objects.get(max_id='max-2')

        self.assertNotEqual(bytes(first.personal_salt), bytes(second.personal_salt))
        self.assertNotEqual(
            bytes(first.personal_key_encrypted),
            bytes(second.personal_key_encrypted),
        )
