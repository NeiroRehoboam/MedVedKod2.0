from django.contrib.auth import get_user_model
from django.test import TestCase

from anamnesis.models import (
    Anamnesis,
    PatientAllergy,
    PatientChronicDisease,
    PatientMedication,
)
from patients.models import Patient

User = get_user_model()


class AnamnesisEncryptionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(max_id="anamnesis-owner", password=None)
        self.patient = Patient.objects.create(user=self.user)

    def test_notes_are_encrypted_at_rest(self):
        anamnesis = Anamnesis.objects.create(
            patient=self.patient,
            recent_events_notes="Операция в марте 2024 года",
        )

        raw = Anamnesis.objects.values_list(
            "recent_events_notes_encrypted", flat=True
        ).get(id=anamnesis.id)
        self.assertNotIn("Операция", raw)
        self.assertEqual(
            Anamnesis.objects.get(id=anamnesis.id).recent_events_notes,
            "Операция в марте 2024 года",
        )

    def test_custom_names_are_encrypted_at_rest(self):
        anamnesis = Anamnesis.objects.create(patient=self.patient)
        medication = PatientMedication.objects.create(
            anamnesis=anamnesis,
            custom_name="Препарат Х",
        )
        allergy = PatientAllergy.objects.create(
            anamnesis=anamnesis,
            custom_name="Пыльца берёзы",
        )
        disease = PatientChronicDisease.objects.create(
            anamnesis=anamnesis,
            custom_name="Хронический гастрит",
        )

        for model, obj, plaintext in (
            (PatientMedication, medication, "Препарат Х"),
            (PatientAllergy, allergy, "Пыльца берёзы"),
            (PatientChronicDisease, disease, "Хронический гастрит"),
        ):
            raw = model.objects.values_list(
                "custom_name_encrypted", flat=True
            ).get(id=obj.id)
            self.assertNotIn(plaintext, raw)
            self.assertEqual(model.objects.get(id=obj.id).custom_name, plaintext)
