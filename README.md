# Nexus — Autonomous AI Research Workspace

> **Стек:** Next.js 15 + FastAPI + Pydantic v2 + SSE  
> **Период:** Октябрь–Ноябрь 2026  
> **Статус:** 🟡 В разработке (День 1)

---

## 🧠 Суть проекта

**Nexus** — это AI-воркспейс для глубокого ресёрча, вдохновлённый Perplexity AI и Google Deep Research.

Пользователь задаёт сложный вопрос (не просто «что такое X», а «сравни архитектуры A и B с точки зрения производительности при highload»). Вместо того чтобы просто отправить запрос к LLM и ждать — Nexus **думает у тебя на глазах**:

1. Разбивает сложный вопрос на подзапросы (query decomposition)
2. Параллельно обрабатывает каждый подзапрос (asyncio.gather)
3. Стримит статус-события в реальном времени (SSE)
4. Начинает стримить итоговый ответ токен за токеном ещё до завершения всех подзапросов
5. При отмене пользователем — мгновенно убивает все async-задачи без лишних расходов

**Это не AI-обёртка с одной кнопкой. Это инженерная система.**

---

## 🎯 Killer Demo Features

### #1 — «Живой Мозг» (главная фича)
На экране появляются карточки подзадач с live-прогрессом:
```
🔍 Analyzing query...        [✓ done]
📡 Searching: "topic A"      [████░░ 65%]
📡 Searching: "topic B"      [██░░░░ 30%]
📡 Searching: "comparison"   [░░░░░░  0%]
✍️  Generating answer...     ← токены стримятся сюда
```
Визуальный эффект: система «думает», а не просто крутит спиннер.

### #2 — «Abort & Cost Guard»
Пользователь жмёт «Стоп» посреди генерации:
- Фронт: `AbortController.abort()` → закрывает SSE-соединение
- Бэк: FastAPI ловит `asyncio.CancelledError` → отменяет все подзапросы
- **Демо-эффект:** в логах видно, что после нажатия «Стоп» ни один токен больше не тратится

---

## 🏗️ Архитектура

```
Browser (Next.js 15)
│
│  POST /api/research  ←── ResearchRequest { query, depth }
│  ← SSE stream ──────────── StreamEvent { event, data, timestamp }
│
FastAPI Backend
│
├── POST /api/research
│     ├── validate (Pydantic v2)
│     ├── decompose_query()     → ["sub-query 1", "sub-query 2", ...]
│     ├── asyncio.gather(       → параллельный сбор данных
│     │     fetch_source(sq1),
│     │     fetch_source(sq2),
│     │   )
│     └── async_generator()     → yield SSE events
│
└── Streaming via StreamingResponse(media_type="text/event-stream")
```

### SSE Event Types
| Тип | Когда | Пример data |
|-----|-------|-------------|
| `STATUS` | Статус выполнения шага | `"Analyzing query..."` |
| `SUB_QUERY` | Новый подзапрос создан | `"What is X?"` |
| `SOURCE` | Найден источник | `{"url": "...", "title": "..."}` |
| `TOKEN` | Кусок итогового ответа | `"The main difference"` |
| `DONE` | Стрим завершён | `""` |
| `ERROR` | Ошибка | `"LLM timeout after 30s"` |

---

## 📁 Структура файлов

```
01_nexus/
├── README.md                   ← этот файл (полное ТЗ)
│
├── backend/
│   ├── pyproject.toml          ← зависимости (fastapi, pydantic, uvicorn, httpx)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             ← FastAPI app, CORS, роуты
│   │   ├── schemas.py          ← Pydantic модели (ResearchRequest, StreamEvent)
│   │   ├── research/
│   │   │   ├── __init__.py
│   │   │   ├── decomposer.py   ← query → list[sub_queries]
│   │   │   ├── fetcher.py      ← async fetch sources per sub-query
│   │   │   └── generator.py    ← async_generator → SSE events
│   │   └── config.py           ← settings (API keys, CORS origins, timeouts)
│   └── tests/
│       ├── test_schemas.py
│       └── test_research.py
│
└── frontend/                   ← Next.js 15 (начнём в ноябре)
    ├── app/
    │   ├── page.tsx            ← главная страница (search input)
    │   └── research/
    │       └── [id]/
    │           └── page.tsx    ← страница результата (live stream UI)
    ├── components/
    │   ├── SearchBox.tsx
    │   ├── ResearchStream.tsx  ← главный компонент, читает SSE
    │   ├── SubQueryCard.tsx    ← карточка подзадачи с прогрессом
    │   └── SourceList.tsx      ← найденные источники
    └── lib/
        └── stream.ts           ← утилиты для чтения SSE (ReadableStream, TextDecoder)
```

---

## 📦 Технический Стек

| Слой | Технология | Зачем |
|------|-----------|-------|
| Frontend | Next.js 15 (App Router) | RSC + Client streaming |
| UI компоненты | shadcn/ui + Tailwind | Без ручного CSS |
| Backend | FastAPI (async) | StreamingResponse, async generators |
| Валидация | Pydantic v2 | Строгие контракты, 422 на невалидные данные |
| HTTP-клиент | httpx (async) | Параллельные запросы к источникам |
| LLM | OpenAI / Gemini API | Генерация ответа |
| Протокол стриминга | SSE (text/event-stream) | Сервер → клиент, нативный HTTP |

---

## 🗓️ Этапы Разработки

### Этап 1 — Фундамент Backend (День 1, сегодня)
- [ ] `schemas.py` — `ResearchRequest`, `StreamEventType`, `StreamEvent`
- [ ] `main.py` — FastAPI app, CORS, `POST /api/research` с фейковым async-генератором
- [ ] Проверка: `curl` видит поток SSE-событий
- [ ] Проверка: невалидный запрос → 422

### Этап 2 — Реальная Логика Backend (Дни 2–5)
- [ ] `decomposer.py` — разбивка запроса на подзапросы
- [ ] `fetcher.py` — `asyncio.gather` для параллельного сбора
- [ ] `generator.py` — полный async-генератор с real LLM
- [ ] `config.py` — settings через `pydantic-settings`
- [ ] Обработка `asyncio.CancelledError` (Abort Guard)
- [ ] Тесты: `tests/test_schemas.py`, `tests/test_research.py`

### Этап 3 — Frontend (Дни 6–14)
- [ ] `SearchBox.tsx` — форма с валидацией
- [ ] `stream.ts` — читаем SSE через `ReadableStream` + `TextDecoderStream`
- [ ] `ResearchStream.tsx` — основной компонент, управление состоянием потока
- [ ] `SubQueryCard.tsx` — живые карточки подзадач
- [ ] `SourceList.tsx` — список источников
- [ ] AbortController — кнопка «Стоп»

### Этап 4 — Полировка (Дни 15–20)
- [ ] Обработка сетевых ошибок и реконнект SSE
- [ ] Оптимизация: `useRef` вместо `useState` для стриминг-буфера
- [ ] Тесты на фронте (vitest)
- [ ] README с GIF-демо
- [ ] Deploy: Vercel (frontend) + Railway/Render (backend)

---

## ⚡ Быстрый старт (когда backend готов)

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Тест стриминга
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare REST vs GraphQL for highload APIs", "depth": "deep"}'
```

---

## 📐 Ключевые Инженерные Решения (ADR)

### Почему SSE, а не WebSockets?
- Поток **однонаправленный** (сервер → клиент). WebSockets для этого избыточны.
- SSE работает поверх обычного HTTP/2 — нет накладных расходов на upgrade.
- Нативный авто-реконнект в браузере (`EventSource` API).
- WebSockets — это Pulse (следующий проект), где нужна двусторонняя связь.

### Почему async generator вместо обычного endpoint?
- Размер ответа неизвестен до завершения генерации.
- Нельзя держать соединение открытым и копить весь ответ в памяти.
- `StreamingResponse` с async generator = zero-copy потоковая передача байтов напрямую в TCP-сокет.

### Почему Pydantic v2 для SSE-событий?
- `.model_dump_json()` в v2 работает через Rust-движок, в 5–10x быстрее v1.
- Строгие контракты: если `StreamEventType.TOKEN` пришёл без `data` — ошибка на этапе сериализации, не в рантайме продакшена.
