from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from ai_assis.models import Session
from patients.models import Patient
from routing.models import RoutingResult

User = get_user_model()


class RoutingResultApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(max_id='owner', password=None)
        self.other = User.objects.create_user(max_id='other', password=None)
        self.session = Session.objects.create(
            patient=Patient.objects.create(user=self.user)
        )
        other_session = Session.objects.create(
            patient=Patient.objects.create(user=self.other)
        )
        self.mine = RoutingResult.objects.create(
            session=self.session,
            urgency=RoutingResult.Urgency.PLANNED,
            justification='own',
            recommendations='own',
        )
        self.foreign = RoutingResult.objects.create(
            session=other_session,
            urgency=RoutingResult.Urgency.PLANNED,
            justification='foreign',
            recommendations='foreign',
        )
        self.client = APIClient()

    def test_anonymous_is_denied(self):
        response = self.client.get(reverse('routing-results-list'))
        self.assertIn(response.status_code, (401, 403))

    def test_owner_sees_only_own_results(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('routing-results-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [self.mine.id])

    def test_foreign_result_is_not_retrievable(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('routing-results-detail', args=[self.foreign.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_own_result_is_retrievable(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse('routing-results-detail', args=[self.mine.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['justification'], 'own')

    def test_text_is_encrypted_at_rest(self):
        justification, recommendations = RoutingResult.objects.values_list(
            'justification_encrypted', 'recommendations_encrypted'
        ).get(id=self.mine.id)

        self.assertNotIn('own', justification)
        self.assertNotIn('own', recommendations)
        stored = RoutingResult.objects.get(id=self.mine.id)
        self.assertEqual(stored.justification, 'own')
        self.assertEqual(stored.recommendations, 'own')

    def test_write_methods_are_disabled(self):
        self.client.force_authenticate(user=self.user)
        list_url = reverse('routing-results-list')
        detail_url = reverse('routing-results-detail', args=[self.mine.id])
        self.assertEqual(self.client.post(list_url, {}, format='json').status_code, 405)
        self.assertEqual(self.client.put(detail_url, {}, format='json').status_code, 405)
        self.assertEqual(self.client.patch(detail_url, {}, format='json').status_code, 405)
        self.assertEqual(self.client.delete(detail_url).status_code, 405)
