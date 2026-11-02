import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from app.research.decomposer import decompose_query
from app.schemas import ResearchRequest, StreamEvent, StreamEventType

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
        def format_sse(event_type: StreamEventType, data: str) -> str:
            event = StreamEvent(event=event_type, data=data)
            return f"data: {event.model_dump_json()}\n\n"

        tokens = ["This ", "is ", "a ", "streamed ", "response."]
        yield format_sse(StreamEventType.STATUS, "Analyzing query...")
        sub_queries = await decompose_query(body.query)
        for sq in sub_queries:
            yield format_sse(StreamEventType.STATUS, f"Sub-task: {sq}")
        await asyncio.sleep(0.5)
        yield format_sse(
            StreamEventType.STATUS,
            f"Searching sources for '{body.query}'...",
        )
        for token in tokens:
            yield format_sse(StreamEventType.TOKEN, token)
            await asyncio.sleep(0.1)
        yield format_sse(StreamEventType.DONE, "")

    return StreamingResponse(generate_events(), media_type="text/event-stream")
