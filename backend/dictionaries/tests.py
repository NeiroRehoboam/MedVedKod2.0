from io import StringIO

from django.apps import apps
from django.core.management import call_command
from django.test import TestCase

from .models import (
    AllergyReference,
    AllergyType,
    ChronicDisease,
    ComplaintCategory,
    HereditaryDisease,
    MedicationReference,
    PaymentType,
    Specialty,
)


class SeedDictionariesTests(TestCase):
    def seed(self):
        call_command("seed_dictionaries", stdout=StringIO())

    def test_populates_all_dictionaries(self):
        self.seed()

        examples = (
            (ChronicDisease, "Артериальная гипертензия"),
            (HereditaryDisease, "Гемофилия"),
            (AllergyReference, "Пыльца берёзы"),
            (MedicationReference, "Парацетамол"),
            (AllergyType, "Пищевая"),
            (Specialty, "Терапевт"),
            (PaymentType, "ОМС"),
            (ComplaintCategory, "Головная боль"),
        )
        for model, name in examples:
            with self.subTest(model=model.__name__):
                self.assertTrue(model.objects.filter(name=name).exists())

    def test_repeated_run_does_not_change_records(self):
        self.seed()
        models = apps.get_app_config("dictionaries").get_models()
        before = {
            model: list(model.objects.order_by("pk").values())
            for model in models
        }

        self.seed()

        for model, records in before.items():
            with self.subTest(model=model.__name__):
                self.assertEqual(list(model.objects.order_by("pk").values()), records)

    def test_preserves_existing_records_and_inactive_flags(self):
        medication = MedicationReference.objects.create(name="Парацетамол", active=False)
        custom_medication = MedicationReference.objects.create(name="Тестовый препарат")
        category = ComplaintCategory.objects.create(
            code="headache", name="Существующая категория", active=False,
        )
        disease = ChronicDisease.objects.create(name="Артериальная гипертензия")

        self.seed()

        medication.refresh_from_db()
        category.refresh_from_db()
        self.assertFalse(medication.active)
        self.assertEqual(MedicationReference.objects.filter(name=medication.name).count(), 1)
        self.assertTrue(MedicationReference.objects.filter(pk=custom_medication.pk).exists())
        self.assertEqual(category.name, "Существующая категория")
        self.assertFalse(category.active)
        self.assertEqual(ComplaintCategory.objects.filter(code="headache").count(), 1)
        self.assertEqual(ChronicDisease.objects.get(name=disease.name).pk, disease.pk)

    def test_does_not_create_patient_or_session_data(self):
        other_models = [
            model for model in apps.get_models()
            if model._meta.app_label != "dictionaries"
        ]
        before = {model: model.objects.count() for model in other_models}

        self.seed()

        for model, count in before.items():
            with self.subTest(model=model._meta.label):
                self.assertEqual(model.objects.count(), count)


