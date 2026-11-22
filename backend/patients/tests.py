from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from patients.models import Patient

User = get_user_model()


@override_settings(PERSONAL_DATA_PEPPER='test-pepper')
class PatientDiagnosisEncryptionTests(TestCase):
    def _login(self, client, max_id, token):
        profile = {
            '_id': max_id,
            'full_name': {'firstName': 'Иван', 'lastName': 'Иванов'},
        }
        with patch('auth_max.views.get_user_by_token', return_value=profile):
            return client.post(
                reverse('max-login'),
                {'token': token},
                content_type='application/json',
            )

    def test_diagnosis_is_encrypted_and_available_only_with_personal_key(self):
        client = APIClient()
        self.assertEqual(self._login(client, 'max-1', 'max-token-1').status_code, 200)

        patient = Patient.objects.get(user=User.objects.get(max_id='max-1'))
        response = client.patch(
            reverse('patient-detail', args=[patient.pk]),
            {'diagnosis': 'Сахарный диабет'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['diagnosis_value'], 'Сахарный диабет')
        patient_id = patient.pk

        patient.refresh_from_db()
        self.assertNotEqual(patient.diagnosis_encrypted, 'Сахарный диабет')

        detail = client.get(reverse('patient-detail', args=[patient_id]))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['diagnosis_value'], 'Сахарный диабет')

        other_client = APIClient()
        self.assertEqual(self._login(other_client, 'max-2', 'max-token-2').status_code, 200)
        forbidden = other_client.get(reverse('patient-detail', args=[patient_id]))
        self.assertEqual(forbidden.status_code, 404)

    def test_jwt_without_max_session_cannot_read_diagnosis(self):
        self.assertEqual(self._login(APIClient(), 'max-1', 'max-token-1').status_code, 200)
        user = User.objects.get(max_id='max-1')

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(reverse('patient-list'))
        self.assertEqual(response.status_code, 403)
