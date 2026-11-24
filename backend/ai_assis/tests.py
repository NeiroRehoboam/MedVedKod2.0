from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from ai_assis import services as ai_services
from ai_assis.models import BaseQuestion, Session
from patients.models import Patient
from routing.models import RoutingResult

User = get_user_model()


class AiSessionApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(max_id="test-user", password=None)
        self.patient = Patient.objects.create(user=self.user)
        BaseQuestion.objects.create(text="Что вас беспокоит?", order=1)
        BaseQuestion.objects.create(text="Как давно?", order=2)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _start(self):
        response = self.client.post(reverse("start-session"))
        self.assertEqual(response.status_code, 201)
        return response.data

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    def test_start_retrieve_and_initial_question(self, _generate):
        data = self._start()
        for key in ("status", "session", "questions", "safety", "next_question"):
            self.assertIn(key, data)
        self.assertEqual(len(data["questions"]), 2)
        self.assertEqual(data["safety"]["danger_status"], "no_critical_signs_detected")

        session_id = data["session"]["id"]
        for url in (
            reverse("sessions-detail", args=[session_id]),
            reverse("session-initial-question", args=[session_id]),
        ):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["questions"], data["questions"])

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    def test_message_saves_answer_and_returns_six_ai_questions(self, mock_generate):
        data = self._start()
        session_id = data["session"]["id"]
        question_id = data["questions"][0]["id"]

        response = self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Болит поясница", "question_id": question_id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["safety"]["is_dangerous"], False)
        self.assertEqual(len(response.data["ai_questions"]), 6)
        self.assertEqual(response.data["next_question"]["source"], "AI")
        self.assertEqual(
            Session.objects.get(id=session_id).questions.get(id=question_id).answer_text,
            "Болит поясница",
        )

        # Шесть сохранённых вопросов пересылаются при следующем ответе, а не генерируются заново.
        second = self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Три дня назад"},
            format="json",
        )
        mock_generate.assert_called_once()
        self.assertEqual([q["id"] for q in second.data["ai_questions"]],
                         [q["id"] for q in response.data["ai_questions"]])

    @override_settings(AI_QUESTION_COUNT=10)
    def test_ai_question_batch_can_be_ten(self):
        data = self._start()
        session_id = data["session"]["id"]
        response = self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Болит поясница", "question_id": data["questions"][0]["id"]},
            format="json",
        )
        self.assertEqual(len(response.data["ai_questions"]), 10)

    def test_dangerous_answer_to_ai_question_stops_session(self):
        data = self._start()
        session_id = data["session"]["id"]
        self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Насморк", "question_id": data["questions"][0]["id"]},
            format="json",
        )
        response = self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Сильная давящая боль в груди, тяжело дышать"},
            format="json",
        )
        self.assertEqual(response.data["status"], "COMPLETED")
        self.assertTrue(response.data["safety"]["is_dangerous"])
        self.assertEqual(
            RoutingResult.objects.get(session_id=session_id).urgency,
            RoutingResult.Urgency.EMERGENCY,
        )

    def test_dangerous_message_stops_session(self):
        data = self._start()
        session_id = data["session"]["id"]

        response = self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Сильная давящая боль в груди, тяжело дышать"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["safety"]["is_dangerous"])
        self.assertTrue(response.data["safety"]["should_stop"])
        self.assertEqual(response.data["status"], "COMPLETED")
        self.assertEqual(
            RoutingResult.objects.get(session_id=session_id).urgency,
            RoutingResult.Urgency.EMERGENCY,
        )

    @patch("rag_module.triage.safety_rules.check_message_with_rules")
    def test_uncertain_rules_do_not_stop_survey(self, mock_rules):
        mock_rules.return_value = SimpleNamespace(
            danger_status="uncertain",
            reason="Сообщение неполное, отсутствует конкретная медицинская информация.",
            matched_rules=(),
        )
        result = ai_services.check_message_safety("Болит голова", use_llm=False)
        self.assertEqual(result["danger_status"], "uncertain")
        self.assertFalse(result["is_dangerous"])
        self.assertFalse(result["should_stop"])

    def test_failed_check_still_stops_survey(self):
        result = ai_services._fallback_safety("Не удалось выполнить проверку.")
        self.assertEqual(result["danger_status"], "uncertain")
        self.assertTrue(result["should_stop"])

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    def test_uncertain_llm_verdict_keeps_session_in_progress(self, _generate):
        uncertain = ai_services._safety(
            danger_status="uncertain",
            urgency="undetermined",
            reason="Сообщение неполное, отсутствует конкретная медицинская информация.",
            recommended_action="Пожалуйста, уточните ваш симптом или состояние.",
            should_stop=True,
        )
        self.assertFalse(uncertain["should_stop"])

        with patch("ai_assis.views.check_message_safety", return_value=uncertain), patch(
            "ai_assis.views.get_session_safety", return_value=uncertain
        ):
            data = self._start()
            session_id = data["session"]["id"]
            response = self.client.post(
                reverse("send-message", args=[session_id]),
                {"content": "Болит голова", "question_id": data["questions"][0]["id"]},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "IN_PROGRESS")
        self.assertEqual(response.data["safety"]["danger_status"], "uncertain")
        self.assertFalse(response.data["safety"]["should_stop"])
        self.assertEqual(len(response.data["ai_questions"]), 6)
        self.assertEqual(Session.objects.get(id=session_id).status, Session.Status.IN_PROGRESS)
        self.assertFalse(RoutingResult.objects.filter(session_id=session_id).exists())

    @patch("ai_assis.views.generate_recommendation")
    def test_complete_creates_routing_result(self, mock_recommendation):
        mock_recommendation.return_value = {
            "source": "test",
            "recommendation": "Обратитесь к врачу",
            "justification": "По данным опроса",
            "urgency": "planned",
            "doctor": "",
            "place": "",
            "evidence": [],
        }
        data = self._start()
        session_id = data["session"]["id"]
        self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Насморк", "question_id": data["questions"][0]["id"]},
            format="json",
        )

        response = self.client.post(reverse("complete-session", args=[session_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "COMPLETED")
        self.assertIn("recommendation", response.data)
        self.assertEqual(
            RoutingResult.objects.get(session_id=session_id).urgency,
            RoutingResult.Urgency.PLANNED,
        )

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    def test_other_user_cannot_access_session(self, _generate):
        session_id = self._start()["session"]["id"]
        other = User.objects.create_user(max_id="other-user", password=None)
        client = APIClient()
        client.force_authenticate(user=other)
        self.assertEqual(client.get(reverse("sessions-detail", args=[session_id])).status_code, 404)

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    @patch("ai_assis.views.generate_recommendation")
    def test_completed_session_result_is_available_on_reopen(self, mock_recommendation, _generate):
        mock_recommendation.return_value = {
            "source": "test",
            "recommendation": "Обратитесь к врачу",
            "justification": "По данным опроса",
            "urgency": "planned",
            "doctor": "",
            "place": "",
            "evidence": [],
        }
        data = self._start()
        session_id = data["session"]["id"]
        self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Насморк", "question_id": data["questions"][0]["id"]},
            format="json",
        )
        self.assertEqual(
            self.client.post(reverse("complete-session", args=[session_id])).status_code,
            200,
        )

        detail = self.client.get(reverse("sessions-detail", args=[session_id]))
        self.assertEqual(detail.data["status"], "COMPLETED")
        self.assertEqual(detail.data["routing"]["recommendations"], "Обратитесь к врачу")
        self.assertEqual(detail.data["recommendation"]["recommendation"], "Обратитесь к врачу")

        result = self.client.get(reverse("session-result", args=[session_id]))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["session"]["id"], session_id)
        self.assertEqual(result.data["routing"]["urgency"], "PLANNED")
        self.assertEqual(result.data["recommendation"]["source"], "stored")

    def test_result_is_not_available_for_in_progress_session(self):
        session_id = self._start()["session"]["id"]
        response = self.client.get(reverse("session-result", args=[session_id]))
        self.assertEqual(response.status_code, 404)

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    def test_other_user_cannot_read_session_result(self, _generate):
        session_id = self._start()["session"]["id"]
        other = User.objects.create_user(max_id="other-user-result", password=None)
        client = APIClient()
        client.force_authenticate(user=other)
        self.assertEqual(
            client.get(reverse("session-result", args=[session_id])).status_code,
            404,
        )

    def test_anonymous_is_forbidden(self):
        self.assertEqual(APIClient().post(reverse("start-session")).status_code, 403)
