import uuid
from django.utils import timezone
from .models import Sessii, VoprosySessii, BystryeOtvety, StatusSessii, IstochnikVoprosa
from patients.models import Patsienty
from .utils import encrypt_data

class SessionService:
    @staticmethod
    def start_session(patsient_max_id: str, session_name: str) -> Sessii:
        patsient, _ = Patsienty.objects.get_or_create(
            max_id=patsient_max_id,
            defaults={"id": uuid.uuid4()},
        )
        return Sessii.objects.create(
            id=uuid.uuid4(),
            patsient=patsient,
            nazvanie=encrypt_data(session_name),
            status=StatusSessii.V_PROTSESSE,
        )

    @staticmethod
    def add_question(sessiya_id: str, text: str, source: str, order: int, answers: list[str] | None = None) -> VoprosySessii:
        vopros = VoprosySessii.objects.create(
            id=uuid.uuid4(),
            sessiya_id=sessiya_id,
            tekst_voprosa=encrypt_data(text),
            istochnik=source or IstochnikVoprosa.SISTEMA,
            poryadkovyy_nomer=order,
        )
        if answers:
            for idx, ans in enumerate(answers):
                BystryeOtvety.objects.create(
                    id=uuid.uuid4(),
                    vopros=vopros,
                    tekst=encrypt_data(ans),
                    poryadkovyy_nomer=idx,
                )
        return vopros