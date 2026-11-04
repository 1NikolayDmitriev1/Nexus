import asyncio

from pydantic import BaseModel, Field


class SourceResult(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    title: str
    url: str
    snippet: str


async def fetch_single_source(query: str) -> SourceResult:
    await asyncio.sleep(0.3)
    return SourceResult(
        query=query,
        title=f"Result for: {query}",
        url=f"https://search.local?q={query}",
        snippet=f"Simulated content extracted for '{query}'",
    )


async def fetch_all_sources(queries: list[str]) -> list[SourceResult]:
    tasks = [fetch_single_source(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return list(results)
