import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "http://qdrant:6333"
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "medical_documents"
)

VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "384"))

GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")

GIGACHAT_SCOPE = os.getenv(
    "GIGACHAT_SCOPE",
    "GIGACHAT_API_PERS"
)

GIGACHAT_MODEL = os.getenv(
    "GIGACHAT_MODEL",
    "GigaChat-2"
)