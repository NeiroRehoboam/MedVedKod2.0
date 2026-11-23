import re

from razdel import sentenize

from rag_module.embeddings.embedding_service import embedding_service


CHUNK_SIZE = 1200
MIN_CHUNK_SIZE = 300

# Начальный порог смыслового сходства.
# Будем подбирать его после тестирования PDF.
SIMILARITY_THRESHOLD = 0.65

def is_section_heading(text: str) -> bool:
    """Проверяет, является ли текст заголовком раздела."""

    text = text.strip()

    patterns = [
        r"^\d+\.\d+\.\s+[А-ЯЁ]",
        r"^[А-ЯЁ\s]{10,}$",
        r"^\d+\.\s+[А-ЯЁ][А-ЯЁ\s]{8,}$"
    ]

    return any(re.match(pattern, text) for pattern in patterns)

def clean_page_text(text: str) -> str:
    """Очищает текст страницы."""

    text = re.sub(r"(?m)^\s*\d{1,4}\s*$", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def get_page_range(start: int, end: int, page_ranges: list[dict]):
    """Находит страницы, из которых взят чанк."""

    chunk_pages = [
        item["page"]
        for item in page_ranges
        if item["start"] < end and item["end"] > start
    ]

    if not chunk_pages:
        return None

    return min(chunk_pages), max(chunk_pages)


def split_long_sentence(text: str, start: int, end: int) -> list[dict]:
    """Разбивает слишком длинное предложение на части."""

    result = []

    while end - start > CHUNK_SIZE:
        cut = start + CHUNK_SIZE

        # Стараемся разрезать по пробелу
        space_position = text.rfind(" ", start, cut)

        if space_position > start:
            cut = space_position

        result.append({
            "start": start,
            "end": cut,
            "text": text[start:cut].strip()
        })

        start = cut

        while start < end and text[start].isspace():
            start += 1

    if start < end:
        result.append({
            "start": start,
            "end": end,
            "text": text[start:end].strip()
        })

    return result


def split_pages_semantically(pages: list[dict]) -> list[dict]:
    """Разбивает текст PDF по смысловой близости предложений."""

    # 1. Объединяем страницы и сохраняем их границы
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
            "page": page["page"]
        })

        full_text += "\n\n"

    if not full_text.strip():
        return []

    # 2. Выделяем предложения
    sentences = []

    for sentence in sentenize(full_text):
        start = sentence.start
        end = sentence.stop

        if not full_text[start:end].strip():
            continue

        # Слишком длинные предложения дополнительно делим
        if end - start > CHUNK_SIZE:
            sentences.extend(
                split_long_sentence(full_text, start, end)
            )
        else:
            sentences.append({
                "start": start,
                "end": end,
                "text": full_text[start:end].strip()
            })

    if not sentences:
        return []

    # 3. Создаём эмбеддинги предложений
    sentence_texts = [item["text"] for item in sentences]

    vectors = embedding_service.encode_documents(sentence_texts)

    # 4. Объединяем соседние предложения по смыслу
    raw_chunks = []

    current_start = sentences[0]["start"]
    current_end = sentences[0]["end"]

    for i in range(1, len(sentences)):

        sentence = sentences[i]

        previous_vector = vectors[i - 1]
        current_vector = vectors[i]

        similarity = sum(
            a * b
            for a, b in zip(previous_vector, current_vector)
        )

        combined_size = sentence["end"] - current_start

        semantic_break = similarity < SIMILARITY_THRESHOLD
        size_break = combined_size > CHUNK_SIZE
        heading_break = is_section_heading(sentence["text"])

        if semantic_break or size_break or heading_break:

            raw_chunks.append({
                "start": current_start,
                "end": current_end
            })

            current_start = sentence["start"]

        current_end = sentence["end"]

    # Добавляем последний чанк
    raw_chunks.append({
        "start": current_start,
        "end": current_end
    })

    # 5. Объединяем маленькие чанки, если хватает места
    # merged_chunks = []

    # for chunk in raw_chunks:

    #     if merged_chunks:
    #         previous = merged_chunks[-1]

    #         combined_size = chunk["end"] - previous["start"]

    #         if (
    #             chunk["end"] - chunk["start"] < MIN_CHUNK_SIZE
    #             and combined_size <= CHUNK_SIZE
    #         ):
    #             previous["end"] = chunk["end"]
    #             continue

    #     merged_chunks.append(chunk)
# 5. Сохраняем смысловые границы чанков
    merged_chunks = raw_chunks
    # 6. Формируем результат и определяем страницы
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
            "chunk_index": chunk_index
        })

    return result
