from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from app.research.generator import generate_research_stream
from app.schemas import ResearchRequest

app = FastAPI(title="Nexus API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/research")
async def research_endpoint(body: ResearchRequest):
    async def generate_events():
        async for event in generate_research_stream(body.query):
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(generate_events(), media_type="text/event-stream")
