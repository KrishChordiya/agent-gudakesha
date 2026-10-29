from pathlib import Path
import os
import tempfile

ROOT = Path.cwd().resolve()

def read_file(file_path: str) -> str:
    """Read a UTF-8 text file and return its contents."""
    path = (ROOT / file_path).resolve()

    if not path.is_relative_to(ROOT):
        return "Error: Access denied"

    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        return f"Error: {e}"

def write_file(file_path: str, content: str) -> str:
    """Safely write an allowed Markdown file."""

    path = (ROOT / file_path).resolve()

    if not path.is_relative_to(ROOT):
        return "Error: Access denied"

    temporary = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=ROOT,
            prefix=".preferences-",
            suffix=".tmp",
            delete=False
        ) as f:
            temporary = Path(f.name)
            f.write(content)

        os.replace(temporary, path)
        return f"Successfully wrote {file_path}"

    except OSError as e:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        return f"Error: {e}"

# def edit_o


READ_FILE_TOOL = {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the specified file path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        }
    }

WRITE_FILE_TOOL = {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create a new file or overwrite an existing file with the specified content at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write into the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    }