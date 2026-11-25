from rag_module import index_document
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


documents_dir = Path(__file__).resolve().parent / "documents"
pdf_files = list(documents_dir.rglob("*.pdf"))

print(f"Найдено документов: {len(pdf_files)}")

for index, file in enumerate(pdf_files, start=1):
    print(f"\n[{index}/{len(pdf_files)}] Индексация: {file.name}")

    try:
        index_document(str(file))
        print("Успешно!")
    except Exception:
        print(f"Ошибка индексации: {file.name}")

print("\nИндексация завершена")
