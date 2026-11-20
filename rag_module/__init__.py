
def search(question: str, limit: int = 5) -> list[dict]:
    """Ищет наиболее релевантные фрагменты документов."""
    from rag_module.retrieval.retriever import search_documents

    return search_documents(question, limit)


def ask(question: str, limit: int = 5) -> str:
    """Ищет информацию в документах и формирует ответ."""
    from rag_module.retrieval.retriever import search_documents
    from rag_module.generation.generator import generate_answer

    search_results = search_documents(question, limit)

    return generate_answer(question, search_results)


def index_document(filename: str) -> dict:
    """Индексирует PDF-документ."""
    from rag_module.processing.indexer import index_pdf

    return index_pdf(filename)
