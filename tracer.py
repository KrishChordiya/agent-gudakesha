
import asyncio
import json
import os
import tempfile

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Tracer:
    def __init__(self, session_id: str, directory: str = "traces"):
        self.session_id = session_id
        self.directory = Path(directory)
        self.path = self.directory / f"session_{session_id}.json"

        self.events: list[dict[str, Any]] = []

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    async def load(self):
        """Load previous events from this session, if any."""
        if not await asyncio.to_thread(self.path.exists):
            return

        def read():
            return json.loads(self.path.read_text(encoding="utf-8"))

        data = await asyncio.to_thread(read)

        if data.get("session_id") != self.session_id:
            raise ValueError("Trace session ID mismatch")

        self.events = data["events"]

    def record_user(self, turn_id: int, content: str):
        self.events.append({
            "type": "user_input",
            "turn_id": turn_id,
            "timestamp": self.timestamp(),
            "content": content
        })

    def record_model(
        self,
        turn_id: int,
        reasoning: str,
        content: str | None,
        tool_calls: list,
        usage: dict,
        duration_ms: float,
        status: str = "success",
        error_message: str | None = None
    ):
        self.events.append({
            "type": "model_call",
            "turn_id": turn_id,
            "timestamp": self.timestamp(),
            "status": status,
            "reasoning": reasoning,
            "content": content,
            "tool_calls": tool_calls,
            "usage": usage,
            "duration_ms": duration_ms,
            "error_message": error_message
        })

    def record_tool(
        self,
        turn_id: int,
        tool_call_id: str,
        name: str,
        arguments: dict,
        result: Any,
        duration_ms: float
    ):
        self.events.append({
            "type": "tool_call",
            "turn_id": turn_id,
            "timestamp": self.timestamp(),
            "tool_call_id": tool_call_id,
            "name": name,
            "arguments": arguments,
            "status": result.status,
            "data": result.data,
            "error_message": result.error_message,
            "error_code": result.error_code,
            "duration_ms": duration_ms
        })

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "events": self.events
        }

    async def save(self):
        """Atomically save the complete session trace."""
        data = self.to_dict()

        def write():
            self.directory.mkdir(parents=True, exist_ok=True)

            temporary = None

            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.directory,
                    prefix=".trace-",
                    suffix=".tmp",
                    delete=False
                ) as f:
                    temporary = Path(f.name)
                    json.dump(
                        data,
                        f,
                        indent=2,
                        ensure_ascii=False
                    )

                os.replace(temporary, self.path)

            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)

        await asyncio.to_thread(write)
