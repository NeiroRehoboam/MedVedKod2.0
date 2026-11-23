from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from rag_module.config import (
    QDRANT_URL,
    COLLECTION_NAME,
    VECTOR_SIZE
)


client = QdrantClient(url=QDRANT_URL)


def check_connection():
    client.get_collections()
    return True


def create_collection():
    if client.collection_exists(COLLECTION_NAME):
        return False

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )

    return True