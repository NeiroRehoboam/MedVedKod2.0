import fitz
from pathlib import Path


def load_pdf(file_path: str) -> list[dict]:
    """
    Извлекает текст из PDF.
    Возвращает текст отдельно для каждой страницы.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Поддерживаются только PDF-файлы")

    pages = []

    with fitz.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "text": text,
                    "page": page_number
                })

    return pages