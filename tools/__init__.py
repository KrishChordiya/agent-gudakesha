from .file import READ_FILE_TOOL, WRITE_FILE_TOOL, read_file, write_file
from .bash import BASH_TOOL, execute_bash
from .web import WEB_SEARCH_TOOL, web_search

TOOLS = [
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    BASH_TOOL,
    WEB_SEARCH_TOOL
]


TOOL_REGISTRY = {
    "read_file": read_file,
    "write_file": write_file,
    "execute_bash": execute_bash,
    "web_search": web_search
}


async def execute_tool(name: str, args: dict) -> str:
    """Execute a registered asynchronous tool."""
    tool = TOOL_REGISTRY.get(name)

    if tool is None:
        return f"Error: unknown tool {name}"

    try:
        return await tool(**args)
    except Exception as e:
        return f"Error executing {name}: {e}"
