import asyncio
import uuid
from typing import Any
from dataclasses import dataclass, field

@dataclass
class Session:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    messages: list[dict[str, Any]] = field(default_factory=list)
    lock: asyncio.Lock = field(
        default_factory=asyncio.Lock,
        repr=False
    )