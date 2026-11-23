
from rag_module.embeddings.embedding_service import embedding_service
from rag_module.database.qdrant import client, COLLECTION_NAME
from rag_module.reranking.reranker import reranker


def search_documents(
    question: str,
    limit: int = 5
) -> list[dict]:

    if not question.strip():
        raise ValueError("Вопрос не может быть пустым")

    # 1. Преобразуем вопрос в embedding
    query_vector = embedding_service.encode_query(question)

    # 2. Получаем кандидатов из Qdrant
    candidate_limit = min(max(limit * 4, 20), 100)

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=candidate_limit,
        with_payload=True
    )

    # 3. Подготавливаем найденные фрагменты
    candidates = []

    for point in response.points:
        payload = point.payload or {}
        text = payload.get("text", "")

        if not text.strip():
            continue

        candidates.append({
            "document_id": payload.get("document_id"),
            "title": payload.get("title"),
            "file": payload.get("file"),
            "page": payload.get("page"),
            "page_start": payload.get("page_start"),
            "page_end": payload.get("page_end"),
            "chunk_index": payload.get("chunk_index"),
            "text": text,
            "qdrant_score": point.score
        })

    if not candidates:
        return []

    # 4. Переранжируем найденные фрагменты
    texts = [item["text"] for item in candidates]

    rerank_scores = reranker.rerank(question, texts)

    # 5. Добавляем оценки Reranker
    for item, score in zip(candidates, rerank_scores):
        item["rerank_score"] = score

    # 6. Сортируем по оценке Reranker
    candidates.sort(
        key=lambda item: item["rerank_score"],
        reverse=True
    )

    # 7. Возвращаем лучшие результаты
    return candidates[:limit]
