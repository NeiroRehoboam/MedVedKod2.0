from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient

from ai_assis import services as ai_services
from ai_assis.models import BaseQuestion, BaseQuestionOption, Session, SessionQuestion
from ai_assis.serializers import SessionQuestionSerializer
from anamnesis.models import (
    Anamnesis,
    PatientAllergy,
    PatientChronicDisease,
    PatientMedication,
)
from dictionaries.models import (
    AllergyReference,
    ChronicDisease,
    MedicationReference,
    PaymentType,
)
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
    def test_options_are_snapshotted_at_start_and_survive_base_changes(self, _generate):
        base = BaseQuestion.objects.get(text="Что вас беспокоит?")
        BaseQuestionOption.objects.create(question=base, text="Болит голова", order=1)

        data = self._start()
        self.assertEqual(data["questions"][0]["options"][0]["text"], "Болит голова")
        self.assertEqual(data["next_question"]["options"], data["questions"][0]["options"])

        question = SessionQuestion.objects.get(id=data["questions"][0]["id"])
        self.assertEqual(question.options[0]["text"], "Болит голова")

        base.is_active = False
        base.save(update_fields=["is_active"])
        response = self.client.get(
            reverse("sessions-detail", args=[data["session"]["id"]])
        )
        self.assertEqual(
            response.data["questions"][0]["options"],
            data["questions"][0]["options"],
        )

    def test_openapi_describes_options_as_array_of_option_objects(self):
        schema = SchemaGenerator().get_schema(request=None, public=True)
        options = schema["components"]["schemas"]["SessionQuestion"]["properties"]["options"]
        self.assertEqual(options["type"], "array")
        self.assertIn("$ref", options["items"])

    def test_options_fallback_to_base_question_for_old_sessions(self):
        base = BaseQuestion.objects.create(
            text="Старый вопрос", order=3, is_multiple_choice=True
        )
        BaseQuestionOption.objects.create(question=base, text="Вариант", order=1)
        base.is_active = False
        base.save(update_fields=["is_active"])
        session = Session.objects.create(patient=self.patient)
        question = SessionQuestion.objects.create(
            session=session,
            question_text="Старый вопрос",
            order_number=1,
            source=SessionQuestion.Source.SYSTEM,
        )

        options = SessionQuestionSerializer(question).data["options"]
        self.assertEqual(options[0]["text"], "Вариант")

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    def test_session_response_includes_preferred_payment(self, _generate):
        payment = PaymentType.objects.create(name="Тестовая оплата")
        self.patient.preferred_payment = payment
        self.patient.save(update_fields=["preferred_payment"])

        data = self._start()
        self.assertEqual(data["preferred_payment"]["id"], payment.id)
        self.assertEqual(data["preferred_payment"]["name"], "Тестовая оплата")

        response = self.client.get(
            reverse("sessions-detail", args=[data["session"]["id"]])
        )
        self.assertEqual(response.data["preferred_payment"]["id"], payment.id)

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
    def test_ai_questions_have_empty_options(self, _generate):
        data = self._start()
        session_id = data["session"]["id"]
        response = self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Болит поясница", "question_id": data["questions"][0]["id"]},
            format="json",
        )
        self.assertEqual(len(response.data["ai_questions"]), 6)
        self.assertTrue(all(q["options"] == [] for q in response.data["ai_questions"]))
        self.assertEqual(response.data["next_question"]["options"], [])

    @patch(
        "ai_assis.views.generate_next_questions",
        return_value=[
            {"question": "Вопрос с вариантами?", "options": ["Да", "Нет"]},
            *[{"question": f"Вопрос {i}?", "options": []} for i in range(2, 7)],
        ],
    )
    def test_ai_options_are_saved_and_returned(self, _generate):
        data = self._start()
        session_id = data["session"]["id"]
        response = self.client.post(
            reverse("send-message", args=[session_id]),
            {"content": "Болит поясница", "question_id": data["questions"][0]["id"]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        ai_question = next(
            q for q in response.data["ai_questions"]
            if q["question_text"] == "Вопрос с вариантами?"
        )
        self.assertEqual(
            [(option["text"], option["order"]) for option in ai_question["options"]],
            [("Да", 1), ("Нет", 2)],
        )
        self.assertGreater(ai_question["options"][0]["id"], 0)
        self.assertNotEqual(
            ai_question["options"][0]["id"],
            ai_question["options"][1]["id"],
        )

        self.assertEqual(
            [option["text"] for option in response.data["next_question"]["options"]],
            ["Да", "Нет"],
        )

        stored = SessionQuestion.objects.get(id=ai_question["id"])
        self.assertEqual([option["text"] for option in stored.options], ["Да", "Нет"])

    def test_old_negative_ai_option_ids_are_returned_positive(self):
        session = Session.objects.create(patient=self.patient)
        question = SessionQuestion.objects.create(
            session=session,
            question_text="Старый AI-вопрос",
            order_number=3,
            source=SessionQuestion.Source.AI,
            options=[{"id": -301, "text": "Да", "order": 1}],
        )

        options = SessionQuestionSerializer(question).data["options"]
        self.assertEqual(options[0]["id"], ai_services.AI_OPTION_ID_OFFSET + 301)
        self.assertEqual(SessionQuestion.objects.get(id=question.id).options[0]["id"], -301)

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

    @patch("ai_assis.views.generate_next_questions", return_value=[f"Вопрос {i}?" for i in range(1, 7)])
    def test_edit_answer_updates_stored_answer(self, _generate):
        data = self._start()
        session_id = data["session"]["id"]
        question_id = data["questions"][0]["id"]
        safe = ai_services._safety(
            danger_status="no_critical_signs_detected",
            urgency="undetermined",
            reason="Критических признаков не найдено.",
            recommended_action="Продолжайте опрос.",
            should_stop=False,
        )
        with patch("ai_assis.views.check_message_safety", return_value=safe), patch(
            "ai_assis.views.get_session_safety", return_value=safe
        ):
            response = self.client.post(
                reverse("send-message", args=[session_id]),
                {"content": "Болит поясница", "question_id": question_id},
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            edited = self.client.patch(
                reverse("session-answer-update", args=[session_id, question_id]),
                {"answer_text": "Болит голова"},
                format="json",
            )

        self.assertEqual(edited.status_code, 200)
        self.assertEqual(edited.data["status"], "IN_PROGRESS")
        self.assertEqual(
            Session.objects.get(id=session_id).questions.get(id=question_id).answer_text,
            "Болит голова",
        )
        self.assertFalse(RoutingResult.objects.filter(session_id=session_id).exists())

    def test_edit_answer_rejected_for_completed_session(self):
        session_id = self._start()["session"]["id"]
        session = Session.objects.get(id=session_id)
        session.status = Session.Status.COMPLETED
        session.save(update_fields=['status'])

        response = self.client.patch(
            reverse("session-answer-update", args=[session_id, session.questions.first().id]),
            {"answer_text": "Другое"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_other_user_cannot_edit_answer(self):
        data = self._start()
        session_id = data["session"]["id"]
        question_id = data["questions"][0]["id"]
        other = User.objects.create_user(max_id="other-user-edit", password=None)
        client = APIClient()
        client.force_authenticate(user=other)

        response = client.patch(
            reverse("session-answer-update", args=[session_id, question_id]),
            {"answer_text": "Чужой текст"},
            format="json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Session.objects.get(id=session_id).questions.get(id=question_id).answer_text,
            None,
        )

    def test_edit_answer_rejects_empty_text(self):
        data = self._start()
        session_id = data["session"]["id"]
        question_id = data["questions"][0]["id"]

        response = self.client.patch(
            reverse("session-answer-update", args=[session_id, question_id]),
            {"answer_text": ""},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_anonymous_is_forbidden(self):
        self.assertEqual(APIClient().post(reverse("start-session")).status_code, 403)


class DeidentificationIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            max_id="id-987654",
            password=None,
            first_name="Анна",
            last_name="Иванова",
        )
        self.patient = Patient.objects.create(
            user=self.user,
            first_name="Анна",
            last_name="Иванова",
            birth_date=date(1990, 5, 12),
        )
        self.session = Session.objects.create(patient=self.patient)
        self.question = SessionQuestion.objects.create(
            session=self.session,
            question_text="Что вас беспокоит?",
            answer_text=(
                "Я Анна Иванова, id-987654, род. 12.05.1990, "
                "тел. +7 999 123-45-67, почта anna@example.com, "
                "температура 38.5, давление 120/80"
            ),
            order_number=1,
        )

    def test_build_answers_replaces_identifiers_with_age(self):
        answer = ai_services.build_answers(self.session)[0]["answer"]
        age = ai_services._age_years(date(1990, 5, 12))

        self.assertNotIn("Анна", answer)
        self.assertNotIn("Иванова", answer)
        self.assertNotIn("id-987654", answer)
        self.assertNotIn("12.05.1990", answer)
        self.assertNotIn("anna@example.com", answer)
        self.assertIn(f"пациенту {age} {ai_services._years_word(age)}", answer)
        self.assertIn("38.5", answer)
        self.assertIn("120/80", answer)
        self.assertTrue(
            SessionQuestion.objects.get(id=self.question.id).answer_text.startswith("Я Анна")
        )

    def test_build_answers_includes_deidentified_anamnesis_context(self):
        anamnesis = Anamnesis.objects.create(
            patient=self.patient,
            smoking_status=Anamnesis.SmokingStatus.CURRENT,
            alcohol_status=Anamnesis.AlcoholStatus.NEVER,
            recent_events_notes="Анна Иванова per 12.05.1990Operations",
        )
        medication = MedicationReference.objects.create(name="Аспирин")
        allergy = AllergyReference.objects.create(name="Пенициллин")
        disease = ChronicDisease.objects.create(name="Астма")
        PatientMedication.objects.create(
            anamnesis=anamnesis, medication=medication,
            intake_mode=PatientMedication.IntakeMode.CONSTANT,
        )
        PatientAllergy.objects.create(anamnesis=anamnesis, allergen=allergy)
        PatientChronicDisease.objects.create(anamnesis=anamnesis, disease=disease)

        with_default = ai_services.build_answers(self.session)
        with_context = ai_services.build_answers(
            self.session, include_anamnesis=True
        )

        self.assertEqual(len(with_default), 1)
        self.assertEqual(len(with_context), 2)
        self.assertEqual(with_context[0]["question"], "Анамнез пациента (фон)")
        context = with_context[0]["answer"]
        self.assertIn("курение: сейчас", context)
        self.assertIn("алкоголь: никогда", context)
        self.assertIn("Аспирин", context)
        self.assertIn("Пенициллин", context)
        self.assertIn("Астма", context)
        self.assertNotIn("Анна", context)
        self.assertNotIn("Иванова", context)
        self.assertNotIn("12.05.1990", context)

        safety = ai_services.get_session_safety(self.session)
        self.assertEqual(safety["danger_status"], "no_critical_signs_detected")

    @patch("ai_assis.services.build_answers", return_value=[])
    def test_rag_callers_request_anamnesis_context(self, mock_build):
        safety = ai_services._safety(
            danger_status="no_critical_signs_detected",
            urgency="undetermined",
            reason="Без критических признаков.",
            recommended_action="Продолжайте опрос.",
        )

        with patch("rag_module.process_patient_answers", return_value={}):
            ai_services.generate_recommendation(self.session, safety)
        self.assertTrue(mock_build.call_args.kwargs.get("include_anamnesis"))

        mock_build.reset_mock()
        with patch("rag_module.config.GIGACHAT_CREDENTIALS", None):
            ai_services.generate_next_questions(self.session, count=1)
        self.assertTrue(mock_build.call_args.kwargs.get("include_anamnesis"))

    @patch("rag_module.config.GIGACHAT_CREDENTIALS", "test-credential")
    def test_safety_check_receives_deidentified_message(self):
        mock_rag_check = MagicMock(
            return_value=SimpleNamespace(
                model_dump=lambda: {
                    "danger_status": "no_critical_signs_detected",
                    "urgency": "undetermined",
                    "reason": "Без критических признаков.",
                    "recommended_action": "Продолжайте опрос.",
                }
            )
        )
        fake_module = SimpleNamespace(check_message_safety=mock_rag_check)

        with patch.dict(
            "sys.modules",
            {"rag_module.triage.message_safety_checker": fake_module},
        ):
            result = ai_services.check_message_safety(
                "Анна Иванова, 12.05.1990, +7 999 123-45-67, болит голова",
                patient=self.patient,
            )
        sent_message = mock_rag_check.call_args.args[0]

        self.assertNotIn("Анна", sent_message)
        self.assertNotIn("Иванова", sent_message)
        self.assertNotIn("12.05.1990", sent_message)
        self.assertNotIn("+7 999", sent_message)
        self.assertIn("болит голова", sent_message)
        self.assertFalse(result["is_dangerous"])

    @patch("rag_module.config.GIGACHAT_CREDENTIALS", "test-credential")
    def test_generated_question_is_deidentified(self):
        mock_generate = MagicMock(
            return_value={"question": "Анна, у вас больно в 12.05.1990?"}
        )
        fake_module = SimpleNamespace(generate_next_question=mock_generate)

        with patch.dict(
            "sys.modules",
            {"rag_module.generation.question_generator": fake_module},
        ):
            questions = ai_services.generate_next_questions(self.session, count=1)

        self.assertNotIn("Анна", questions[0]["question"])
        self.assertNotIn("12.05.1990", questions[0]["question"])

    @patch("rag_module.config.GIGACHAT_CREDENTIALS", "test-credential")
    def test_generated_options_are_kept_and_deidentified(self):
        mock_generate = MagicMock(
            return_value={
                "question": "Каквариант для Анны?",
                "options": ["Анна", "  Болит  ", "Анна", ""],
            }
        )
        fake_module = SimpleNamespace(generate_next_question=mock_generate)

        with patch.dict(
            "sys.modules",
            {"rag_module.generation.question_generator": fake_module},
        ):
            questions = ai_services.generate_next_questions(self.session, count=1)

        self.assertEqual(
            questions[0]["options"],
            ["[ИМЯ]", "Болит"],
        )

    def test_answer_is_encrypted_at_rest(self):
        raw = SessionQuestion.objects.values_list(
            "answer_text_encrypted", flat=True
        ).get(id=self.question.id)

        self.assertNotIn("Анна", raw)
        self.assertNotIn("болит", raw)
        self.assertEqual(
            SessionQuestion.objects.get(id=self.question.id).answer_text,
            self.question.answer_text,
        )

    @patch("rag_module.config.GIGACHAT_CREDENTIALS", "test-credential")
    def test_failed_safety_check_does_not_log_patient_text(self):
        def explode(message):
            raise RuntimeError(f"Ошибка на тексте: {message}")

        fake_module = SimpleNamespace(check_message_safety=explode)
        with patch.dict(
            "sys.modules",
            {"rag_module.triage.message_safety_checker": fake_module},
        ):
            with self.assertLogs("ai_assis.services", level="WARNING") as captured:
                result = ai_services.check_message_safety(
                    "Анна Иванова, 12.05.1990, болит голова",
                    patient=self.patient,
                )

        self.assertTrue(
            all(
                "Анна" not in line
                and "Иванова" not in line
                and "болит" not in line
                for line in captured.output
            )
        )
        self.assertEqual(result["danger_status"], "no_critical_signs_detected")
