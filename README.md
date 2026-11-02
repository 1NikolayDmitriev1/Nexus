# Nexus

An autonomous research workspace that breaks down complex questions, searches sources in parallel, and streams structured answers in real time.

Built with **Next.js 15**, **FastAPI**, **Pydantic v2**, and **Server-Sent Events (SSE)**.

---

## Why I Built This

Most AI projects today are simple wrappers:
1. User clicks a button.
2. The server blocks for 10–15 seconds while a model generates text.
3. The client dumps the entire response onto the screen all at once.

If the user closes the tab midway through? The server keeps burning expensive API tokens in the background anyway. If the question is multi-faceted? The model hallucinates or misses key angles because it tried to do everything in one monolithic prompt.

**Nexus takes a different approach:**
- **Breaks questions down:** When you ask something complex (*"Compare Kafka vs RabbitMQ for IoT message ingestion"*), Nexus decomposes it into 3–4 focused sub-queries.
- **Parallel execution:** Sub-queries run concurrently via `asyncio`, fetching references without blocking the event loop.
- **Progressive streaming:** You see the "thought process" live — sub-tasks pop up, sources attach as they are found, and the final answer streams token-by-token.
- **Immediate cancellation:** If you navigate away or click stop, the frontend aborts the HTTP connection (`AbortController`), and FastAPI catches `asyncio.CancelledError` to kill all in-flight tasks instantly. No wasted compute.

---

## Architecture

Here is how data flows through the system:

```text
Browser (Next.js 15)
   │
   │  1. POST /api/research  {"query": "...", "depth": "quick"}
   │
   ▼
FastAPI Backend
   │
   ├── Validates payload (Pydantic v2, strips spaces, checks length)
   │
   ├── Decomposes query into sub-tasks (decomposer.py)
   │
   ├── Runs async workers in parallel (fetcher.py)
   │
   └── Streams events back as they happen (text/event-stream)
          │
          ├─► data: {"event": "STATUS", "data": "Analyzing query..."}
          ├─► data: {"event": "STATUS", "data": "Sub-task: Message throughput limits"}
          ├─► data: {"event": "TOKEN",  "data": "Kafka "}
          ├─► data: {"event": "TOKEN",  "data": "handles "}
          └─► data: {"event": "DONE",   "data": ""}
```

---

## Stream Event Types

Every message from the server follows the standard SSE format: `data: <JSON>\n\n`.

| Event | Purpose | Example Payload |
|---|---|---|
| `STATUS` | Pipeline progress updates | `{"event": "STATUS", "data": "Searching sources..."}` |
| `SOURCE` | A resolved link or citation | `{"event": "SOURCE", "data": "https://..."}` |
| `TOKEN` | A single chunk of generated text | `{"event": "TOKEN", "data": "latency"}` |
| `DONE` | Research complete | `{"event": "DONE", "data": ""}` |
| `ERROR` | Recoverable or fatal error | `{"event": "ERROR", "data": "Source timeout"}` |

---

## Key Engineering Decisions

### Why SSE instead of WebSockets?
Nexus only needs to send data **one way** (from server to client). 
- WebSockets require protocol upgrading, keep-alive pings, and a stateful connection server.
- Server-Sent Events run over standard HTTP/2. They give us automatic reconnection, zero custom proxy configuration, and native browser support via `EventSource` or `fetch` streams without extra overhead.

### Why Async Generators with `StreamingResponse`?
Instead of buffering an entire 5KB response in Python memory before sending it, the endpoint uses an `async def` generator with `yield`. 
Each chunk is pushed directly into the TCP socket the moment it is ready. This keeps memory usage at $O(1)$ per user and drops **Time To First Token (TTFT)** down to milliseconds.

### Strict Schemas (Pydantic v2)
Every single event flying through the wire is validated through Pydantic v2 models. Using `model_dump_json()` leverages Pydantic's Rust core, serializing events substantially faster than standard Python `json.dumps` and preventing malformed JSON from ever reaching the client.

---

## Project Structure

```text
01_nexus/
├── README.md               # Main project documentation
├── backend/
│   ├── pyproject.toml      # Python dependencies & config
│   ├── README.md           # Backend setup guide
│   └── app/
│       ├── main.py         # FastAPI entrypoint & SSE streaming route
│       ├── schemas.py      # Pydantic models (ResearchRequest, StreamEvent)
│       └── research/
│           ├── decomposer.py  # Query decomposition logic
│           └── ...
└── frontend/               # Next.js 15 app (work in progress)
```

---

## Running Locally

### Backend Setup

```bash
cd backend

# Activate virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Or on macOS/Linux:
# source .venv/bin/activate

# Install dependencies in editable mode
pip install -e .

# Run dev server
uvicorn app.main:app --reload --port 8000
```

### Quick Test via cURL

Open another terminal and test the live stream:

```bash
curl -N -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare PostgreSQL and MongoDB for time-series data", "depth": "quick"}'
```

You will see events streaming in real time line-by-line.

---

## Status & Roadmap

- [x] Initial FastAPI async backend
- [x] Pydantic v2 contract validation
- [x] SSE streaming endpoint (`POST /api/research`)
- [x] Sub-task decomposition interface
- [ ] Connect live LLM API for decomposition and answer synthesis
- [ ] Parallel async source retrieval (`asyncio.gather`)
- [ ] Next.js 15 frontend with live thought-process cards
- [ ] AbortController wiring for instant client cancellation
- [ ] Automated integration test suite (`pytest`)
