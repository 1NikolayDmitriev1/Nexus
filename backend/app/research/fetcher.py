import asyncio

from duckduckgo_search import DDGS
from pydantic import BaseModel, Field


class SourceResult(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    title: str
    url: str
    snippet: str


def _search_web(query: str) -> SourceResult:
    try:
        with DDGS() as ddgs:
            result = list(ddgs.text(query, backend="lite", max_results=1))
            r = result[0]
            return SourceResult(
                query=query, title=r["title"], url=r["href"], snippet=r["body"]
            )
    except Exception:
        pass
    return SourceResult(
        query=query,
        title=f"Source: {query}",
        url=f"https://duckduckgo.com/?q={query}",
        snippet=f"Information gathered for query: {query}",
    )


async def fetch_single_source(query: str) -> SourceResult:
    return await asyncio.to_thread(_search_web, query)


async def fetch_all_sources(queries: list[str]) -> list[SourceResult]:
    tasks = [fetch_single_source(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return list(results)
