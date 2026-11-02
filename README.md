# Nexus — Autonomous AI Research Workspace

> **Stack:** Next.js 15 (App Router) • FastAPI • Pydantic v2 • Server-Sent Events (SSE)  
> **Target:** Production-Grade AI Research & Knowledge Synthesis Platform  
> **Status:** 🟡 Active Development

---

## 🧠 Overview & Core Philosophy

**Nexus** is an autonomous AI research workspace inspired by modern deep-research tools (e.g., Perplexity AI, Google Deep Research).

Most contemporary AI applications are shallow "wrappers" that execute a blocking `POST` request, display a static loading spinner, and return a plain text dump. Nexus approaches research as an **orchestrated engineering pipeline**:

1. **Query Decomposition:** Breaks complex, ambiguous questions into structured, parallelizable sub-queries.
2. **Concurrent Multi-Source Aggregation:** Fetches and evaluates heterogeneous data sources asynchronously (`asyncio.gather` / `TaskGroup`).
3. **Live Streaming Pipeline:** Emits fine-grained status transitions and tokens to the client in real time via Server-Sent Events (SSE).
4. **Early Output Emission:** Begins streaming synthesized answer tokens before all secondary background tasks finish.
5. **Abort & Resource Guard:** Listens for client disconnects (`AbortSignal`) and cascades cancellation (`asyncio.CancelledError`) across all running coroutines, preventing wasted compute and token expenditure.

---

## 🎯 Killer Demo Features

### 1. "Live Thought Process"
The user interface does not display a generic loader. As soon as a research query is submitted, interactive sub-task cards populate the viewport dynamically:
```text
🔍 Analyzing query...             [✓ done]
📡 Searching: "topic A"           [████░░ 65%]
📡 Searching: "topic B"           [██░░░░ 30%]
📡 Synthesizing findings...       ← Token stream starts here
```
Users observe the system deconstruct problems and synthesize data in real time.

### 2. "Abort & Cost Guard"
When a user closes their browser tab or clicks "Cancel":
- **Client:** `AbortController.abort()` closes the active HTTP SSE connection.
- **Server:** FastAPI detects the socket termination and raises `asyncio.CancelledError`.
- **Worker:** All in-flight HTTP requests and LLM generation tasks terminate immediately. No orphaned background jobs.

---

## 🏗️ Architecture & Data Flow

```text
Browser (Next.js 15 Client)
│
│  POST /api/research  ───────►  Payload: ResearchRequest { query, depth }
│  ◄────── SSE Stream  ────────  Events:  StreamEvent { event, data, timestamp }
│
FastAPI Core (Backend Service)
│
├── 1. Request Ingestion & Validation (Pydantic v2)
│      └── Strips whitespace, validates query boundaries (3..500 chars).
│
├── 2. Query Decomposition Engine
│      └── Transforms root query into targeted sub-tasks.
│
├── 3. Asynchronous Orchestrator
│      └── Spawns concurrent fetch tasks via non-blocking I/O.
│
└── 4. Streaming Response Producer
       └── Yields SSE chunks ("data: {...}\n\n") via Transfer-Encoding: chunked.
```

### Event Specification (SSE Protocol)

| Event Type | Trigger | Data Payload |
|---|---|---|
| `STATUS` | Pipeline milestone reached | Status string (e.g., `"Analyzing query..."`) |
| `SUB_QUERY` | Sub-task defined by decomposer | Sub-query string |
| `SOURCE` | Reference or citation resolved | JSON string with URL and metadata |
| `TOKEN` | Streamed synthesis chunk | Word / token fragment |
| `DONE` | Stream concluded successfully | Empty string / summary metrics |
| `ERROR` | Recoverable or fatal pipeline error | Error message description |

---

## 📁 Repository Structure

```text
01_nexus/
├── README.md                   # System specification & architectural overview
│
├── backend/
│   ├── pyproject.toml          # PEP 621 dependency declarations
│   ├── README.md               # Backend service documentation & runbook
│   ├── app/
│   │   ├── __init__.py         # Package root
│   │   ├── main.py             # FastAPI entrypoint, middleware, SSE routes
│   │   ├── schemas.py          # Pydantic v2 data contracts & validation
│   │   └── research/
│   │       ├── __init__.py
│   │       ├── decomposer.py   # Query decomposition engine
│   │       ├── fetcher.py      # Async concurrent source collector
│   │       └── generator.py    # SSE stream generation logic
│   └── tests/
│       ├── test_schemas.py
│       └── test_api.py
│
└── frontend/                   # Next.js 15 application (planned)
    ├── app/
    │   ├── page.tsx            # Research dashboard
    │   └── layout.tsx
    ├── components/
    │   ├── ResearchStream.tsx  # Core SSE stream consumer
    │   └── SubTaskCard.tsx     # Dynamic progress indicator
    └── lib/
        └── sse.ts              # ReadableStream & TextDecoder wrappers
```

---

## ⚡ Quickstart

### Prerequisites
- Python 3.11+
- Git

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Unix / macOS:
source .venv/bin/activate

# 3. Install dependencies in editable mode
pip install -e .

# 4. Start local development server
uvicorn app.main:app --reload --port 8000
```

### Verification (Live SSE Stream)

```bash
curl -N -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare REST vs gRPC performance in high-throughput microservices", "depth": "quick"}'
```

---

## 📐 Architecture Decision Records (ADR)

### ADR-001: Server-Sent Events (SSE) over WebSockets
- **Context:** The client requires a real-time stream of research steps, citations, and LLM tokens.
- **Decision:** Utilize Server-Sent Events (`text/event-stream`) over HTTP/2.
- **Rationale:** 
  - The communication model is strictly unidirectional (server-to-client).
  - SSE runs over standard HTTP; no protocol upgrade handshakes or specialized proxy configurations required.
  - Built-in automatic reconnection semantics on modern clients.
  - Avoids the stateful socket-server overhead required for WebSockets.

### ADR-002: Async Generators for Zero-Memory Buffering
- **Context:** Total response payload size is indeterminate at invocation time.
- **Decision:** Implement stream endpoints using Python asynchronous generators (`async def` with `yield`) connected to Starlette's `StreamingResponse`.
- **Rationale:** 
  - Eliminates server-side in-memory response buffering.
  - Emits byte packets directly into the TCP socket buffer as soon as coroutines yield data.
  - Minimizes Time To First Token (TTFT) for end users.

### ADR-003: Strict Schema Serialization via Pydantic v2
- **Context:** Streaming events must maintain type safety across backend and frontend layers.
- **Decision:** Use Pydantic v2 `BaseModel` and `.model_dump_json()` for all event formatting.
- **Rationale:** 
  - Rust-based serialization core executes 5-10x faster than Pydantic v1.
  - Guarantees runtime serialization integrity: invalid events fail at production boundaries rather than producing corrupted JSON in browser parsers.
