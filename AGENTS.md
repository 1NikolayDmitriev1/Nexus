# Nexus Enterprise — Engineering Standards (`AGENTS.md`)

> Repository-level engineering rules for AI coding assistants operating inside `projects/01_nexus`.

## 1. Tech Stack & Architecture
- **Backend:** Python 3.14, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async + `asyncpg`), `pgvector`, Alembic, Redis, `pytest-asyncio`.
- **Frontend (planned):** Next.js 15 (App Router), TypeScript strict mode, Tailwind CSS, `shadcn/ui`, TanStack Query.
- **Layer Boundaries (`backend/app/`):**
  - `api/`: HTTP/SSE routers, request validation, auth dependencies. No raw SQL or business logic.
  - `services/`: business workflows, LangGraph orchestration, billing settlement. No FastAPI `Request`/`HTTPException` coupling where avoidable.
  - `repositories/`: async SQLAlchemy queries and database locking (`selectinload`, `FOR UPDATE`).
  - `models/`: SQLAlchemy 2.0 `DeclarativeBase` + `Mapped` models.
  - `schemas/`: Pydantic v2 DTOs (`OpenAPI -> TypeScript` contract-first source of truth).
  - `core/`: config (`pydantic-settings`), async DB engine/session, security primitives.

## 2. Database & Concurrency Invariants
- **Naming & Defaults:** Always attach an explicit `naming_convention` to `Base.metadata` and define both Python defaults and PostgreSQL `server_default` on timestamps/defaults.
- **Enums:** Always pass `create_constraint=True` and `values_callable=lambda obj: [e.value for e in obj]` to `sqlalchemy.Enum(..., native_enum=False)` so PostgreSQL enforces lowercase `CHECK` constraints.
- **Tenant Isolation (IDOR Defense):** Every workspace-owned query (`research_threads`, `messages`, `document_chunks`, `token_ledger`) MUST filter by `workspace_id` and verify membership.
- **Billing & Concurrency:** Never lock aggregates (`SUM()`). Lock the explicit balance row with `SELECT ... FOR UPDATE` and append an immutable audit row to `token_ledger` in the same transaction; use `idempotency_keys` for external payment webhooks and `version_id` (`409 Conflict`) for OCC.

## 3. AI Security, Async & Code Hygiene
- **English Only:** All code, comments, docstrings, schema descriptions, and commit messages MUST be strictly in English.
- **Indirect Prompt Injection:** Always wrap untrusted external/document snippets in `<context>...</context>` delimiters with explicit instructions forbidding instruction execution from context.
- **Timeouts & Cancellation:** Wrap external I/O (LLM, web fetch, Stripe) in timeouts; offload blocking calls with `asyncio.to_thread`; catch `asyncio.CancelledError` cleanly in streaming generators and re-raise after cleanup.
- **No Silent Failures:** Never write `except Exception: pass` or fabricate synthetic search sources when upstream retrieval fails.
- **SSE Headers:** Include `"Cache-Control": "no-cache"` and `"X-Accel-Buffering": "no"` on `StreamingResponse` SSE endpoints.
