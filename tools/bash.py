import asyncio
from .model import BashArgs

async def execute_bash(args:BashArgs) -> str:
    """Execute a shell command asynchronously."""
    
    process = await asyncio.create_subprocess_shell(
        args.command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=args.timeout
    )

    output = stdout.decode(errors="replace")

    if stderr:
        output += f"\n[stderr]:\n{stderr.decode(errors='replace')}"

    if process.returncode != 0:
        output += f"\n[exit code]: {process.returncode}"

    return output.strip() or "Command executed successfully with no output."

# Schema
BASH_TOOL = {
    "type": "function",
    "function": {
        "name": "execute_bash",
        "description": "Run a shell command in the local environment and return the output.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute"
                },
                "timeout":{
                    "type":"number",
                    "description":"Time (in seconds) to wait for command execution. Defaults to 30s."
                }
            },
            "required": ["command"]
        }
    }
}