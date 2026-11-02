import asyncio


async def decompose_query(query: str) -> list[str]:
    await asyncio.sleep(0.2)
    return [f"1{query}", f"2{query}", f"3{query}"]
