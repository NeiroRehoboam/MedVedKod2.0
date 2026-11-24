from django.test import SimpleTestCase

from rag_module.triage.deidentification import deidentify


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
