# Nexus Backend

The core backend service for Nexus, responsible for orchestrating research queries and streaming real-time events over SSE.

## Stack
- **Python 3.11+**
- **FastAPI** — async routing and streaming endpoints
- **Pydantic v2** — strict schema validation and Rust-powered JSON serialization
- **Uvicorn** — ASGI web server
- **HTTPX** — async HTTP client for concurrent external requests

## Getting Started

### 1. Activate your virtual environment
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

### 2. Start the development server
```powershell
uvicorn app.main:app --reload --port 8000
```

### 3. Test the stream endpoint
```powershell
curl -N -X POST http://localhost:8000/api/research `
  -H "Content-Type: application/json" `
  -d '{"query": "Postgres vs MySQL for JSON queries", "depth": "quick"}'
```

## Directory Overview
- `app/main.py` — FastAPI setup, CORS middleware, and the `/api/research` SSE route.
- `app/schemas.py` — Data models (`ResearchRequest`, `StreamEvent`, `StreamEventType`).
- `app/research/decomposer.py` — Logic that splits a research query into targeted sub-tasks.
