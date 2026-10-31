import asyncio
import json
from ddgs import DDGS


def _search(query: str, max_results: int) -> list:
    """Synchronous search executed in a worker thread."""
    with DDGS() as browser:
        return list(browser.text(query, max_results=max_results))


async def web_search(query: str, max_results: int = 5) -> str:
    """Search the web without blocking the event loop."""
    try:
        results = await asyncio.to_thread(
            _search,
            query,
            max_results
        )

        if not results:
            return "No search results found."

        return json.dumps(results)

    except Exception as e:
        return f"Search error: {e}"

# Schemas
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for real-time information, documentation, or facts.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results":{
                    "type": "number",
                    "description":"Number of results per search. Defaults to 5"
                }
            },
            "required": ["query"]
        }
    }
}