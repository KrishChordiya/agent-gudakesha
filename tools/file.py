import asyncio
import os
import tempfile
from pathlib import Path
from aiofile import async_open

ROOT = Path.cwd().resolve()


def resolve_path(file_path: str) -> Path:
    path = (ROOT / file_path).resolve()

    if not path.is_relative_to(ROOT):
        raise ValueError("Access denied")

    return path


async def read_file(file_path: str) -> str:
    """Read a UTF-8 text file asynchronously."""
    try:
        path = resolve_path(file_path)

        async with async_open(path, "r", encoding="utf-8") as f:
            return await f.read()

    except (OSError, ValueError, UnicodeError) as e:
        return f"Error: {e}"


async def write_file(file_path: str, content: str) -> str:
    """Atomically write a UTF-8 text file."""
    temporary = None

    try:
        path = resolve_path(file_path)

        # Create a unique temporary file in the target directory.
        fd, name = await asyncio.to_thread(
            tempfile.mkstemp,
            prefix=".preferences-",
            suffix=".tmp",
            dir=path.parent
        )
        temporary = Path(name)
        os.close(fd)

        async with async_open(temporary, "w", encoding="utf-8") as f:
            await f.write(content)

        await asyncio.to_thread(os.replace, temporary, path)

        return f"Successfully wrote {file_path}"

    except (OSError, ValueError, UnicodeError) as e:
        return f"Error: {e}"

    finally:
        if temporary is not None:
            await asyncio.to_thread(temporary.unlink, missing_ok=True)


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