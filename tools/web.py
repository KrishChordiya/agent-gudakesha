from ddgs import DDGS
import json

def web_search(query: str, max_results: int = 5):
    """Perform a web search using DuckDuckGo without API keys."""
    try:
        with DDGS() as browser:
            results = [r for r in browser.text(query, max_results=max_results)]
            if not results:
                return "No search results found."
            return json.dumps(results)
    except Exception as e:
        return f"Search error: {str(e)}"

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