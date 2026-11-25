import asyncio
import logging

from ddgs import DDGS
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
FETCH_TIMEOUT_SECONDS = 10.0


class SourceResult(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    title: str
    url: str
    snippet: str


def _search_web(query: str) -> SourceResult | None:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, backend="lite", max_results=1))
        if not results:
            return None
        r = results[0]
        return SourceResult(
            query=query, title=r["title"], url=r["href"], snippet=r["body"]
        )


async def fetch_single_source(query: str) -> SourceResult | None:
    return await asyncio.wait_for(
        asyncio.to_thread(_search_web, query), timeout=FETCH_TIMEOUT_SECONDS
    )


async def fetch_all_sources(queries: list[str]) -> list[SourceResult]:
    tasks = [fetch_single_source(q) for q in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    sources: list[SourceResult] = []
    for query, item in zip(queries, results, strict=True):
        if isinstance(item, asyncio.CancelledError):
            raise item
        if isinstance(item, BaseException):
            logger.warning("Failed to fetch source for query=%r: %s", query, item)
            continue
        if item is not None:
            sources.append(item)
    return sources
