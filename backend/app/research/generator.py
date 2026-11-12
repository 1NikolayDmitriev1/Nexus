import asyncio

from google import genai

from app.config import settings
from app.research.decomposer import decompose_query
from app.research.fetcher import fetch_all_sources
from app.schemas import StreamEvent, StreamEventType


async def generate_research_stream(query: str):

    client = genai.Client(api_key=settings.gemini_api_key)
    sub_queries = await decompose_query(query)
    yield StreamEvent(event=StreamEventType.SOURCE, data={"sub_queries": sub_queries})
    sources = await fetch_all_sources(sub_queries)
    yield StreamEvent(
        event=StreamEventType.SOURCE,
        data={"sources": [s.model_dump() for s in sources]},
    )
    context_parts = []
    for i, s in enumerate(sources, 1):
        context_parts.append(f"[{i}] {s.title}\nURL: {s.url}\nSnippet: {s.snippet}\n")
    context = "\n".join(context_parts)

    prompt = f"""You are an expert research analyst in the Nexus platform.
    Answer the user's question comprehensively and objectively, relying ONLY on the provided sources below.
    Always include inline citations referencing the source numbers in brackets, such as [1], [2].
    If the sources do not contain enough information to answer, state that clearly.

    SOURCES:
    {context}

    USER QUESTION:
    {query}

    ANALYSIS:
    """
    response = await client.aio.models.generate_content_stream(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    async for chunk in response:
        if chunk.text:
            yield StreamEvent(event=StreamEventType.CHUNK, data={"delta": chunk.text})

    yield StreamEvent(event=StreamEventType.DONE)
