# Nexus Backend Service

FastAPI asynchronous orchestration engine for deep query research and real-time SSE streaming.

## Tech Stack
- **Python:** >= 3.11
- **FastAPI:** 0.115+
- **Pydantic:** v2.8+
- **Uvicorn:** 0.30+
- **HTTPX:** 0.27+ (Asynchronous HTTP client)

## Local Runbook

### 1. Environment Setup
```powershell
# Activate local virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2. Start Uvicorn Server
```powershell
uvicorn app.main:app --reload --port 8000
```

### 3. Verify Endpoint via cURL
```powershell
curl -N -X POST http://localhost:8000/api/research `
  -H "Content-Type: application/json" `
  -d '{"query":"Microservices vs Monolith","depth":"quick"}'
```

## Module Structure
- `app/main.py`: Application entrypoint, CORS configuration, and `/api/research` SSE route.
- `app/schemas.py`: Pydantic v2 data models (`ResearchRequest`, `StreamEvent`, `StreamEventType`).
- `app/research/decomposer.py`: Query decomposition and sub-task planning engine.
