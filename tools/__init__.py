from pydantic import ValidationError

from .file import READ_FILE_TOOL, WRITE_FILE_TOOL, read_file, write_file
from .bash import BASH_TOOL, execute_bash
from .web import WEB_SEARCH_TOOL, web_search
from .model import WriteFileArgs, ReadFileArgs, BashArgs, WebSearchArgs, ToolResult

TOOLS = [
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    BASH_TOOL,
    WEB_SEARCH_TOOL
]


TOOL_REGISTRY = {
    "read_file": (read_file, ReadFileArgs),
    "write_file": (write_file, WriteFileArgs),
    "execute_bash": (execute_bash, BashArgs),
    "web_search": (web_search, WebSearchArgs)
}


async def execute_tool(name: str, args: dict) -> ToolResult:
    """Execute a registered asynchronous tool."""
    # Handled here to prevent classifying a KeyError raised inside a tool as an unknown tool.
    try:
        tool, schema = TOOL_REGISTRY[name]
    except KeyError:
        return ToolResult(
            status="error",
            error_message=f"Unknown tool: {name}",
            error_code="UNKNOWN_TOOL"
        )

    validated_args = schema.model_validate(args)
    result = await tool(validated_args)
    return ToolResult(
        status = "success",
        data = result
    )