import subprocess

def execute_bash(command: str, timeout: int = 30):
    """Run a bash command and return stdout/stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]:\n{result.stderr}"
        return output.strip() or "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

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