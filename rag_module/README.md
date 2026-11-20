#  RAG Module

## Требования

- Python 3.12+
- Запущенный Qdrant
- Доступ к GigaChat API

## Установка

Клонируйте репозиторий и перейдите в его папку.

Создайте виртуальное окружение:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Установите библиотеку:

```powershell
pip install -e .
```

## Настройка

Создайте файл `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
```

Укажите свои данные GigaChat в `GIGACHAT_CREDENTIALS`.

Настройте подключение к Qdrant:

- `http://localhost:6333` — если Python запускается на компьютере.
- `http://qdrant:6333` — если библиотека работает в Docker-сети с Qdrant.

Параметры подключения находятся в `.env`.

## Использование

Импортируйте необходимые функции:

```python
from rag_module import search, ask, index_document
```

Индексация PDF:

```python
result = index_document("document.pdf")
```

По умолчанию PDF ищется в папке `documents`.

Поиск информации:

```python
results = search("Что такое сколиоз?", limit=5)
```

Поиск и генерация ответа:

```python
answer = ask(
    "Какие задачи решает ЛФК при сколиозе у детей?",
    limit=5
)
```

## Структура библиотеки

- `__init__.py` — публичные функции библиотеки: `search`, `ask`, `index_document`.
- `config.py` — настройки и переменные окружения.
- `database/` — подключение и работа с Qdrant.
- `document_loader/` — извлечение текста из PDF.
- `embeddings/` — создание векторных представлений текста.
- `processing/` — очистка, разбиение и индексация документов.
- `reranking/` — оценка релевантности найденных фрагментов.
- `retrieval/` — поиск информации в Qdrant.
- `generation/` — формирование ответов через GigaChat.