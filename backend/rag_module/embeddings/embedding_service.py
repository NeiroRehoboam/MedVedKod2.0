from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "intfloat/multilingual-e5-small"
        )

    def encode_documents(self, texts: list[str]):
        prepared_texts = [
            f"passage: {text}" for text in texts
        ]

        vectors = self.model.encode(
            prepared_texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        return vectors.tolist()

    def encode_query(self, text: str):
        prepared_text = f"query: {text}"

        vector = self.model.encode(
            [prepared_text],
            normalize_embeddings=True
        )

        return vector[0].tolist()


embedding_service = EmbeddingService()