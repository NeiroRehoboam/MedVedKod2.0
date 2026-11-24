from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

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
