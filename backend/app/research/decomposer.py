import asyncio

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import settings

LLM_TIMEOUT_SECONDS = 30.0


class DecomposedQueries(BaseModel):
    queries: list[str]


async def decompose_query(query: str) -> list[str]:
    client = genai.Client(api_key=settings.gemini_api_key)
    response = await asyncio.wait_for(
        client.aio.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"Decompose this user query into 3 distinct search sub-queries: {query}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DecomposedQueries,
            ),
        ),
        timeout=LLM_TIMEOUT_SECONDS,
    )
    if response.text is None:
        raise ValueError("Model response is empty or was blocked by safety filters.")

    result = DecomposedQueries.model_validate_json(response.text)
    return result.queries
