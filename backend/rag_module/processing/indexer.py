
from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

from qdrant_client.models import (
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

from rag_module.document_loader.pdf_loader import load_pdf
from rag_module.processing.semantic_chunking import split_pages_semantically
from rag_module.embeddings.embedding_service import embedding_service
from rag_module.database.qdrant import (
    client,
    create_collection,
    COLLECTION_NAME
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = PROJECT_ROOT / "documents"

def index_pdf(filename: str):

    file_path = Path(filename)

    if not file_path.is_absolute():
        file_path = DOCUMENTS_DIR / file_path

    file_path = file_path.resolve()
    document_id = file_path.name

    if not file_path.is_file():
        raise FileNotFoundError("Документ не найден")

    # 1. Читаем PDF
    pages = load_pdf(str(file_path))

    # 2. Разбиваем текст на чанки
    chunks = split_pages_semantically(pages)

    if not chunks:
        raise ValueError("В документе не найден текст")

    # 3. Создаём embeddings
    texts = [chunk["text"] for chunk in chunks]
    vectors = embedding_service.encode_documents(texts)

    # 4. Создаём коллекцию, если её ещё нет
    create_collection()

    # 5. Подготавливаем точки для Qdrant
    points = []

    for chunk, vector in zip(chunks, vectors):

        page_start = chunk["page_start"]
        page_end = chunk["page_end"]

        point_id = str(
            uuid5(
                NAMESPACE_URL,
                f"{document_id}:{page_start}:{chunk['chunk_index']}"
            )
        )

        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "document_id": document_id,
                    "title": Path(filename).stem,
                    "file": document_id,

                    # Для совместимости со старым кодом
                    "page": page_start,

                    # Новый диапазон страниц
                    "page_start": page_start,
                    "page_end": page_end,

                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"]
                }
            )
        )

    # 6. Удаляем старые чанки этого документа
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        ),
        wait=True
    )

    # 7. Сохраняем новые точки партиями
    batch_size = 64

    for start in range(0, len(points), batch_size):
        batch = points[start:start + batch_size]

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
            wait=True
        )

    return {
        "document": filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "indexed": len(points)
    }
