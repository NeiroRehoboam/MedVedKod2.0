from django.apps import AppConfig
from django.db.models.signals import post_migrate

PAYMENT_TYPES = ("ОМС", "ДМС", "Платно")


def seed_payment_types(sender, **kwargs):
    """Заполняет справочник способов оплаты при каждом свежем деплое."""
    PaymentType = sender.get_model("PaymentType")
    for name in PAYMENT_TYPES:
        PaymentType.objects.get_or_create(name=name)


class DictionariesConfig(AppConfig):
    name = 'dictionaries'

    def ready(self):
        post_migrate.connect(seed_payment_types, sender=self, weak=False)
