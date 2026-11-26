import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from rag_module.triage.deidentification import deidentify


class QuestionBatchTests(SimpleTestCase):
    def setUp(self):
        self.answers = [{"question": "Жалоба", "answer": "Болит голова со вчерашнего дня"}]
        self.questions = [
            {"question": text, "options": options} for text, options in (
                ("Где именно болит голова?", ["В висках", "Во лбу", "В затылке"]),
                ("Как меняется боль в течение дня?", ["Слабее", "Так же", "Сильнее"]),
                ("Есть ли тошнота?", ["Да", "Нет", "Не знаю"]),
                ("Усиливается ли боль при ходьбе?", ["Да", "Нет", "Не знаю"]),
                ("Мешает ли боль спать?", ["Да", "Нет", "Не знаю"]),
            )
        ]

    def response(self, questions):
        return SimpleNamespace(messages=[SimpleNamespace(content=[SimpleNamespace(
            text=json.dumps({"known_facts": ["Боль началась вчера"], "questions": [
                {**q, "aspect": aspect} for q, aspect in zip(questions, (
                    "location", "course", "associated_symptom", "triggers", "daily_activity",
                ))
            ]}, ensure_ascii=False),
        )])])

    def generate(self, responses):
        from rag_module.generation import question_generator as generator
        client = MagicMock()
        client.chat.create.side_effect = [*responses, responses[-1]]
        with patch.object(generator, "GIGACHAT_CREDENTIALS", "test"), patch.object(
            generator, "GigaChat",
        ) as factory:
            factory.return_value.__enter__.return_value = client
            result = generator.generate_question_batch(self.answers)
        return result, client

    def test_entire_batch_is_generated_then_reviewed_with_history(self):
        self.answers.insert(0, {"question": "Анамнез", "answer": "Аллергия на пенициллины"})
        result, client = self.generate([self.response(self.questions)])
        self.assertEqual(result, self.questions)
        self.assertEqual(client.chat.create.call_count, 2)
        self.assertIn("ФИНАЛЬНАЯ РЕДАКТОРСКАЯ ПРОВЕРКА", client.chat.create.call_args.args[0].messages[1].content[0].text)
        request = client.chat.create.call_args.args[0]
        prompt = "\n".join(message.content[0].text for message in request.messages)
        self.assertIn("Аллергия на пенициллины", prompt)
        self.assertIn("со вчерашнего дня", prompt)
        self.assertIn("Проверь каждую пару", prompt)
        self.assertIn("Сопоставь каждый вопрос со ВСЕЙ жалобой и анамнезом", prompt)

    def test_duplicate_batch_is_retried_as_a_whole(self):
        duplicate = [self.questions[0]] * 5
        result, client = self.generate([
            self.response(duplicate), self.response(self.questions),
        ])
        self.assertEqual(result, self.questions)
        self.assertEqual(client.chat.create.call_count, 3)

    def test_wrong_count_is_retried(self):
        result, client = self.generate([
            self.response(self.questions[:4]), self.response(self.questions),
        ])
        self.assertEqual(len(result), 5)
        self.assertEqual(client.chat.create.call_count, 3)

    def test_retry_limit_is_bounded(self):
        with self.assertRaises(RuntimeError):
            self.generate([self.response([self.questions[0]] * 5)] * 3)

    def test_empty_options_are_rejected(self):
        invalid = [{**q, "options": []} for q in self.questions]
        result, client = self.generate([self.response(invalid), self.response(self.questions)])
        self.assertEqual(result, self.questions)
        self.assertEqual(client.chat.create.call_count, 3)

    def test_duplicate_options_with_different_case_are_rejected(self):
        invalid = [dict(q) for q in self.questions]
        invalid[0]["options"] = ["Да", " да! ", "Нет"]
        result, client = self.generate([self.response(invalid), self.response(self.questions)])
        self.assertEqual(result, self.questions)
        self.assertEqual(client.chat.create.call_count, 3)

    def test_fallback_questions_also_have_options(self):
        from ai_assis.services import generate_next_questions
        with patch("ai_assis.services.build_answers", return_value=self.answers), patch(
            "rag_module.config.GIGACHAT_CREDENTIALS", None,
        ):
            result = generate_next_questions(SimpleNamespace(patient=None))
        self.assertEqual(len(result), 5)
        for question in result:
            self.assertGreaterEqual(len(question["options"]), 3)
            self.assertEqual(len(question["options"]), len(set(question["options"])))

    def test_options_are_checked_after_normalization(self):
        invalid = [dict(q) for q in self.questions]
        invalid[0]["options"] = ["Нет", " нет! ", "Не знаю"]
        result, client = self.generate([self.response(invalid), self.response(self.questions)])
        self.assertEqual(result, self.questions)
        self.assertEqual(client.chat.create.call_count, 3)

    def test_different_questions_with_same_aspect_are_rejected(self):
        response = self.response(self.questions)
        data = json.loads(response.messages[0].content[0].text)
        data["questions"][1]["aspect"] = data["questions"][0]["aspect"]
        response.messages[0].content[0].text = json.dumps(data)
        result, client = self.generate([response, self.response(self.questions)])
        self.assertEqual(result, self.questions)
        self.assertEqual(client.chat.create.call_count, 3)

    def test_session_adapter_requests_one_batch_and_keeps_api_fields(self):
        from ai_assis.services import generate_next_questions
        with patch("ai_assis.services.build_answers", return_value=self.answers), patch(
            "rag_module.config.GIGACHAT_CREDENTIALS", "test",
        ), patch(
            "rag_module.generation.question_generator.generate_question_batch",
            return_value=self.questions,
        ) as generate:
            result = generate_next_questions(SimpleNamespace(patient=None))
        generate.assert_called_once_with(self.answers, count=5)
        self.assertEqual(result, self.questions)


class RecommendationPresentationTests(SimpleTestCase):
    def test_removes_technical_references_without_removing_clinical_numbers(self):
        from rag_module.generation.recommendation_generator import clean_patient_text
        for reference in (
            "(Источник 2, страница 8)", "[Источник 2, стр. 8]", "[2]",
            "(Источник: КР162_3, страница 8)", "(КР162_3.pdf, стр. 8)",
        ):
            with self.subTest(reference=reference):
                self.assertEqual(
                    clean_patient_text(f"Боль 3 из 10 {reference}."), "Боль 3 из 10.",
                )

    def generate(self, quote):
        from rag_module.generation import recommendation_generator as generator
        text = "Врач-невролог проводит первичный осмотр пациента."
        response = SimpleNamespace(messages=[SimpleNamespace(content=[SimpleNamespace(
            text=json.dumps({
                "doctor": "Невролог", "urgency": "planned", "place": "Поликлиника",
                "recommendation": "Обратитесь к неврологу (Источник 1, страница 8).",
                "reason": "Невролог оценит описанную головную боль [1].",
                "evidence": [{"source": 1, "quote": quote}],
            }, ensure_ascii=False),
        )])])
        client = MagicMock()
        client.chat.create.return_value = response
        with patch.object(generator, "GIGACHAT_CREDENTIALS", "test"), patch.object(
            generator, "GigaChat",
        ) as factory:
            factory.return_value.__enter__.return_value = client
            return generator.generate_recommendation(
                [{"question": "Жалоба", "answer": "Головная боль"}],
                [{"text": text, "title": "КР162_3", "page": 8}],
            )

    def test_patient_text_is_cleaned_and_verified_evidence_is_preserved(self):
        quote = "Врач-невролог проводит первичный осмотр пациента."
        result = self.generate(quote)
        self.assertEqual(result["recommendation"], "Обратитесь к неврологу.")
        self.assertEqual(result["reason"], "Невролог оценит описанную головную боль.")
        self.assertEqual(result["evidence"], [{
            "source": 1, "quote": quote, "document": "КР162_3", "page": 8,
        }])

    def test_unverified_quote_still_rejects_recommendation(self):
        with self.assertRaisesRegex(RuntimeError, "Не удалось подтвердить"):
            self.generate("Эта цитата отсутствует в переданном документе.")


class DeidentificationTests(SimpleTestCase):
    def test_profile_values_are_replaced_with_age(self):
        values = {
            'Анна': '[ИМЯ]',
            'Иванова': '[ИМЯ]',
            '12.05.1990': 'пациенту 36 лет',
        }
        result = deidentify(
            'Анна Иванова родилась 12.05.1990, температура 38.5, давление 120/80',
            values,
        )

        self.assertNotIn('Анна', result)
        self.assertNotIn('Иванова', result)
        self.assertNotIn('12.05.1990', result)
        self.assertIn('пациенту 36 лет', result)
        self.assertIn('38.5', result)
        self.assertIn('120/80', result)

    def test_generic_identifiers_are_masked(self):
        result = deidentify(
            'Телефон +7 999 123-45-67, почта anna@example.com, '
            'СНИЛС 123-456-789 12, паспорт 4510 123456, полис 1234567890123456'
        )

        self.assertIn('[ТЕЛЕФОН]', result)
        self.assertIn('[EMAIL]', result)
        self.assertIn('[СНИЛС]', result)
        self.assertIn('[ПАСПОРТ]', result)
        self.assertIn('[НОМЕР]', result)
        self.assertNotIn('anna@example.com', result)
        self.assertNotIn('1234567890123456', result)

    def test_medical_values_are_kept(self):
        result = deidentify('Температура 38.5, пульс 96, давление 120/80, дата 12.05.1990')

        self.assertIn('38.5', result)
        self.assertIn('96', result)
        self.assertIn('120/80', result)
        self.assertIn('12.05.1990', result)

    def test_deidentification_is_idempotent(self):
        values = {'Анна': '[ИМЯ]', '12.05.1990': 'пациенту 36 лет'}
        once = deidentify('Анна, 12.05.1990, +7 999 123-45-67', values)

        self.assertEqual(deidentify(once, values), once)
