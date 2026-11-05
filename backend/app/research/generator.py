import asyncio

from app.research.decomposer import decompose_query
from app.research.fetcher import fetch_all_sources
from app.schemas import StreamEvent, StreamEventType


async def generate_research_stream(query: str):
    sub_queries = await decompose_query(query)
    yield StreamEvent(event=StreamEventType.SOURCE, data={"sub_queries": sub_queries})
    sources = await fetch_all_sources(sub_queries)
    yield StreamEvent(
        event=StreamEventType.SOURCE,
        data={"sources": [s.model_dump() for s in sources]},
    )
    text = "Based on the gathered sources, here is your comprehensive analysis..."
    words = text.split(" ")
    for word in words:
        await asyncio.sleep(0.05)
        yield StreamEvent(event=StreamEventType.CHUNK, data={"delta": word + " "})

    yield StreamEvent(event=StreamEventType.DONE)
