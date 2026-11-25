from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from consultations.crypto_module import DecryptionError
from dictionaries.models import PaymentType

from .models import Patient

User = get_user_model()


class PatientViewSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(max_id='owner', password=None)
        self.other = User.objects.create_user(max_id='other', password=None)
        self.patient = Patient.objects.create(user=self.user)
        self.foreign = Patient.objects.create(user=self.other)
        self.client = APIClient()

    def test_anonymous_cannot_list(self):
        response = self.client.get(reverse('patient-list'))
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_cannot_retrieve(self):
        response = self.client.get(reverse('patient-detail', args=[self.patient.id]))
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_cannot_create_orphan_card(self):
        response = self.client.post(
            reverse('patient-list'), {'first_name': 'Аноним'}, format='json'
        )
        self.assertIn(response.status_code, (401, 403, 405))
        self.assertFalse(Patient.objects.filter(user__isnull=True).exists())

    def test_owner_sees_only_own_card(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('patient-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [self.patient.id])

    def test_foreign_card_is_not_retrievable(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('patient-detail', args=[self.foreign.id]))
        self.assertEqual(response.status_code, 404)

    def test_write_methods_are_disabled(self):
        self.client.force_authenticate(user=self.user)
        list_url = reverse('patient-list')
        detail_url = reverse('patient-detail', args=[self.patient.id])
        self.assertEqual(self.client.post(list_url, {}, format='json').status_code, 405)
        self.assertEqual(self.client.put(detail_url, {}, format='json').status_code, 405)
        self.assertEqual(self.client.patch(detail_url, {}, format='json').status_code, 405)
        self.assertEqual(self.client.delete(detail_url).status_code, 405)

    def test_diagnosis_is_encrypted_at_rest(self):
        self.patient.diagnosis = 'Артериальная гипертензия'
        self.patient.save()
        self.patient.refresh_from_db()
        self.assertNotIn('Артериальная', self.patient.diagnosis_encrypted)
        self.assertEqual(self.patient.diagnosis, 'Артериальная гипертензия')

    def test_diagnosis_is_bound_to_owner(self):
        self.patient.diagnosis = 'Секрет'
        self.patient.save()
        ciphertext = Patient.objects.get(pk=self.patient.pk).diagnosis_encrypted
        self.foreign.diagnosis_encrypted = ciphertext
        with self.assertRaises(DecryptionError):
            self.foreign.diagnosis


class PreferredPaymentViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(max_id='payer', password=None)
        self.payment = PaymentType.objects.create(name='Тестовое ДМС')
        self.inactive = PaymentType.objects.create(name='Тестовый ОМС', active=False)
        self.client = APIClient()

    def test_anonymous_cannot_change_preferred_payment(self):
        response = self.client.patch(
            reverse('preferred-payment-update'),
            {'preferred_payment': self.payment.id},
            format='json',
        )
        self.assertIn(response.status_code, (401, 403))

    def test_owner_can_set_and_read_preferred_payment(self):
        patient = Patient.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse('preferred-payment-update'),
            {'preferred_payment': self.payment.id},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        patient.refresh_from_db()
        self.assertEqual(patient.preferred_payment_id, self.payment.id)
        self.assertEqual(response.data['preferred_payment_detail']['name'], 'Тестовое ДМС')

    def test_owner_can_clear_preferred_payment(self):
        patient = Patient.objects.create(user=self.user, preferred_payment=self.payment)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse('preferred-payment-update'),
            {'preferred_payment': None},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        patient.refresh_from_db()
        self.assertIsNone(patient.preferred_payment_id)

    def test_inactive_payment_type_is_rejected(self):
        Patient.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse('preferred-payment-update'),
            {'preferred_payment': self.inactive.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('preferred_payment', response.data)

    def test_user_without_patient_card_gets_404(self):
        user = User.objects.create_user(max_id='no-card', password=None)
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            reverse('preferred-payment-update'),
            {'preferred_payment': self.payment.id},
            format='json',
        )
        self.assertEqual(response.status_code, 404)

    def test_other_patient_fields_are_not_writable_here(self):
        patient = Patient.objects.create(user=self.user, first_name='Иван')
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse('preferred-payment-update'),
            {
                'preferred_payment': self.payment.id,
                'first_name': 'Подмена',
                'diagnosis': 'Подмена',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        patient.refresh_from_db()
        self.assertEqual(patient.first_name, 'Иван')
        self.assertFalse(patient.diagnosis)
