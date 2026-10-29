from .file import READ_FILE_TOOL, WRITE_FILE_TOOL, read_file, write_file
from .bash import BASH_TOOL, execute_bash
from .web import WEB_SEARCH_TOOL, web_search

TOOLS = [
    # File
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    # Bash
    BASH_TOOL,
    # Web
    WEB_SEARCH_TOOL
]

def execute_tool(name, args):
    registry = {
        "read_file": read_file,
        "write_file": write_file,
        "execute_bash": execute_bash,
        "web_search": web_search,
    }

    if name in registry:
        try:
            return registry[name](**args)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
    
    return f"Error: unknown tool {name}"