# Gudakesha Agent

Gudakesha ("Conqueror of Sleep" in Sanskrit) is a minimal async AI agent that chats through an OpenRouter-compatible API, executes tools (read/write files, run bash, web search), and records every turn to a trace file.

## Installation

```bash
# Clone the repo
git clone <repo-url>
cd agent-gudakesha

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Copy the example env file and fill in your values
cp .env.example .env
```

Required `.env` values:

```
BASE_URL=https://openrouter.ai/api/v1
MODEL=<your-model>
API_KEY=<your-api-key>
```

## Usage

```bash
python chat.py
```

Type `/exit` to end the session. Each session's events are saved under `traces/`.

## Project structure

- `chat.py` — interactive CLI entry point
- `client.py` — API client with streaming, tool execution, and retry loop
- `session.py` — per-session message history and locking
- `tracer.py` — atomic JSON trace recording per session
- `tools/` — file, bash, web search, and model schemas
- `prompts/SOUL.md` — system prompt