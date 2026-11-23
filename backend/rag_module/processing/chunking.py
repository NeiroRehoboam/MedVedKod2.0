
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
MIN_CHUNK_SIZE = 300


def clean_page_text(text: str) -> str:
    """Очищает текст страницы от номеров и лишних пробелов."""

    text = re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def get_page_range(start: int, end: int, page_ranges: list[dict]):
    """Определяет страницы, текст которых попал в чанк."""

    chunk_pages = [
        item["page"]
        for item in page_ranges
        if item["start"] < end and item["end"] > start
    ]

    if not chunk_pages:
        return None

    return min(chunk_pages), max(chunk_pages)


def split_pages(pages: list[dict]) -> list[dict]:
    """Объединяет страницы, разбивает текст и сохраняет источники."""

    full_text = ""
    page_ranges = []

    for page in pages:
        page_text = clean_page_text(page["text"])

        if not page_text:
            continue

        start = len(full_text)
        full_text += page_text
        end = len(full_text)

        page_ranges.append({
            "start": start,
            "end": end,
            "page": page["page"],
        })

        full_text += "\n\n"

    if not full_text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    documents = splitter.create_documents([full_text])

    raw_chunks = []

    for document in documents:
        start = document.metadata["start_index"]
        end = start + len(document.page_content)

        raw_chunks.append({
            "start": start,
            "end": end,
        })

    # Объединяем маленькие чанки с предыдущими,
    # если общий размер не превышает CHUNK_SIZE.
    merged_chunks = []

    for chunk in raw_chunks:
        if merged_chunks:
            previous = merged_chunks[-1]

            combined_size = chunk["end"] - previous["start"]

            if (
                chunk["end"] - chunk["start"] < MIN_CHUNK_SIZE
                and combined_size <= CHUNK_SIZE
            ):
                previous["end"] = chunk["end"]
                continue

        merged_chunks.append(chunk)

    result = []

    for chunk_index, chunk in enumerate(merged_chunks):
        start = chunk["start"]
        end = chunk["end"]

        page_range = get_page_range(start, end, page_ranges)

        if page_range is None:
            continue

        page_start, page_end = page_range

        result.append({
            "text": full_text[start:end].strip(),
            "page": page_start,
            "page_start": page_start,
            "page_end": page_end,
            "chunk_index": chunk_index,
        })

    return result
