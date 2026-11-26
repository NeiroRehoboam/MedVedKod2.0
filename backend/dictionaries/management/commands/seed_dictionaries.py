from django.core.management.base import BaseCommand
from django.db import transaction

from dictionaries.models import (
    AllergyReference,
    AllergyType,
    ChronicDisease,
    ComplaintCategory,
    HereditaryDisease,
    MedicationReference,
    PaymentType,
    Specialty,
)


DICTIONARIES = {
    ChronicDisease: (
        "Артериальная гипертензия",
        "Ишемическая болезнь сердца",
        "Хроническая сердечная недостаточность",
        "Сахарный диабет 1 типа",
        "Сахарный диабет 2 типа",
        "Бронхиальная астма",
        "Хроническая обструктивная болезнь лёгких",
        "Хронический гастрит",
        "Язвенная болезнь желудка",
        "Хроническая болезнь почек",
        "Гипотиреоз",
        "Ревматоидный артрит",
        "Мигрень",
        "Эпилепсия",
    ),
    HereditaryDisease: (
        "Артериальная гипертензия",
        "Ишемическая болезнь сердца",
        "Инфаркт миокарда",
        "Инсульт",
        "Сахарный диабет 2 типа",
        "Бронхиальная астма",
        "Рак молочной железы",
        "Колоректальный рак",
        "Семейная гиперхолестеринемия",
        "Гемофилия",
        "Муковисцидоз",
        "Поликистоз почек",
    ),
    AllergyReference: (
        "Пенициллины",
        "Цефалоспорины",
        "Ацетилсалициловая кислота",
        "Ибупрофен",
        "Коровье молоко",
        "Куриное яйцо",
        "Арахис",
        "Орехи",
        "Рыба",
        "Морепродукты",
        "Пыльца берёзы",
        "Пыльца злаковых трав",
        "Клещи домашней пыли",
        "Эпителий кошки",
        "Эпителий собаки",
        "Латекс",
        "Яд пчелы",
        "Яд осы",
    ),
    MedicationReference: (
        "Парацетамол",
        "Ибупрофен",
        "Ацетилсалициловая кислота",
        "Амоксициллин",
        "Цетиризин",
        "Лоратадин",
        "Омепразол",
        "Метформин",
        "Инсулин гларгин",
        "Эналаприл",
        "Лозартан",
        "Амлодипин",
        "Бисопролол",
        "Аторвастатин",
        "Левотироксин натрия",
        "Сальбутамол",
        "Будесонид",
    ),
    AllergyType: (
        "Лекарственная",
        "Пищевая",
        "Пыльцевая",
        "Бытовая",
        "Эпидермальная",
        "Инсектная",
        "Контактная",
    ),
    Specialty: (
        "Терапевт",
        "Педиатр",
        "Кардиолог",
        "Невролог",
        "Эндокринолог",
        "Гастроэнтеролог",
        "Пульмонолог",
        "Аллерголог-иммунолог",
        "Оториноларинголог",
        "Офтальмолог",
        "Дерматовенеролог",
        "Хирург",
        "Травматолог-ортопед",
        "Уролог",
        "Акушер-гинеколог",
    ),
    PaymentType: ("ОМС", "ДМС", "Платно"),
}

COMPLAINT_CATEGORIES = (
    ("headache", "Головная боль"),
    ("chest_pain", "Боль в груди"),
    ("fever", "Повышенная температура"),
    ("respiratory", "Кашель и насморк"),
    ("abdominal_pain", "Боль в животе"),
    ("back_pain", "Боль в спине"),
    ("joint_pain", "Боль в суставах"),
    ("skin", "Высыпания и зуд"),
    ("dizziness", "Головокружение"),
    ("other", "Другое"),
)


class Command(BaseCommand):
    help = "Заполняет справочники тестовыми данными, сохраняя существующие записи."

    @transaction.atomic
    def handle(self, *args, **options):
        total_created = 0
        for model, names in DICTIONARIES.items():
            created_count = 0
            for name in names:
                _, created = model.objects.get_or_create(name=name)
                created_count += int(created)
            total_created += created_count
            self.stdout.write(f"{model.__name__}: добавлено {created_count}")

        created_count = 0
        for code, name in COMPLAINT_CATEGORIES:
            _, created = ComplaintCategory.objects.get_or_create(
                code=code, defaults={"name": name},
            )
            created_count += int(created)
        total_created += created_count
        self.stdout.write(f"ComplaintCategory: добавлено {created_count}")
        self.stdout.write(self.style.SUCCESS(f"Готово. Добавлено записей: {total_created}."))
