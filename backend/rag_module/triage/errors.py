from rag_module.triage.models import TriageResult


class TriageBlockedError(RuntimeError):
    """Обычный сценарий остановлен проверкой Triage."""

    def __init__(self, result: TriageResult):
        self.result = result
        super().__init__(result.message)