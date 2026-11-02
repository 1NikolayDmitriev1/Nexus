# Nexus Backend (FastAPI + Async Core)

Сервис оркестрации глубокого ресерча и генерации ответов в режиме реального времени.

## Стек
- **Python:** >= 3.11 (или 3.14)
- **FastAPI:** 0.115+
- **Pydantic:** v2.8+
- **Uvicorn:** 0.30+
- **HTTPX:** 0.27+ (асинхронный HTTP-клиент)

## Локальный запуск

1. Активировать окружение:
```powershell
.\.venv\Scripts\Activate.ps1
```

2. Запуск сервера:
```powershell
uvicorn app.main:app --reload --port 8000
```

3. Быстрый тест стриминга через curl / PowerShell:
```powershell
curl -X POST http://localhost:8000/api/research -H "Content-Type: application/json" -d '{\"query\":\"Microservices vs Monolith\",\"depth\":\"quick\"}'
```

## Структура модуля
- `app/main.py` — роутер, CORS, SSE-эндпоинт `/api/research`
- `app/schemas.py` — Pydantic v2 модели (`ResearchRequest`, `StreamEvent`, `StreamEventType`)
- `app/research/decomposer.py` — декомпозиция сложных запросов на подзадачи
