
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


MODEL_NAME = "BAAI/bge-reranker-v2-m3"


class Reranker:

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Загрузка Reranker на устройство: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME
        )

        self.model.to(self.device)
        self.model.eval()

        print("Reranker успешно загружен")

    def rerank(self, question: str, texts: list[str]) -> list[float]:

        if not texts:
            return []

        pairs = [(question, text) for text in texts]

        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.inference_mode():
            outputs = self.model(**inputs)

        scores = outputs.logits.view(-1).cpu().tolist()

        return scores


reranker = Reranker()
