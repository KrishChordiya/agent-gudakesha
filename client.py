import time
import json
import httpx
import logging

from pydantic import ValidationError
from tools import execute_tool
from tools.model import ToolResult
from tracer import Tracer

# Configure once at app startup
logging.basicConfig(
    level=logging.ERROR,  # must be <= ERROR to see logger.exception() output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get a named logger (use __name__ for module-level context)
logger = logging.getLogger(__name__)

class Client:
    def __init__(self, base_url, model, api_key, tool_executor=None):
        self.model = model
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=180
        )
        
        self.tool_executor = tool_executor or execute_tool


    async def execute_tool(
        self,
        name,
        args,
        tracer,
        turn_id,
        tool_call_id
    ):
        print(f"\nTool Call: {name}: {args}")

        start = time.perf_counter()
        result = None
        try:
            result = await self.tool_executor(name, args)
        
        except ValidationError as e:
            result = ToolResult(
                status="error",
                error_message=str(e),
                error_code="INVALID_TOOL_ARGUMENTS"
            )

        except PermissionError as e:
            result = ToolResult(
                status="error",
                error_message=str(e),
                error_code="ACCESS_DENIED"
            )

        except TimeoutError as e:
            result = ToolResult(
                status="error",
                error_message="Tool execution timed out",
                error_code="TOOL_TIMEOUT"
            )

        except OSError as e:
            result = ToolResult(
                status="error",
                error_message=str(e),
                error_code=f"{name.upper()}_ERROR"
            )

        except LookupError as e:
            result = ToolResult(
                status="error",
                error_message=str(e),
                error_code="INVALID_TOOL_NAME"
            )

        except Exception:
            logger.exception("Unexpected failure executing tool: %s", name)

            result = ToolResult(
                status="error",
                error_message="Unexpected tool executor failure",
                error_code="TOOL_FAILURE"
            )

        finally:
            tracer.record_tool(
                turn_id=turn_id,
                tool_call_id=tool_call_id,
                name=name,
                arguments=args,
                result=result,
                duration_ms=round(
                    (time.perf_counter() - start) * 1000, 2
                )
            )

        return result

        
    async def stream_response(self, payload):
        GRAY = "\033[38;5;245m"
        RESET = "\033[0m"
        content = ""
        tool_calls = {}
        reasoning = ""
        usage = {}
        last_section = None
        async with self.client.stream(
            "POST",
            "chat/completions",
            json=payload
        ) as response:
            response.raise_for_status()

            async for chunk in response.aiter_lines():
                if not chunk.startswith("data:"):
                    continue
                
                data_str = chunk[5:].strip()
                if data_str=="[DONE]":
                    break

                data = json.loads(data_str)

                if data.get("usage") is not None:
                    usage = data["usage"]

                if not data.get("choices"):
                    continue

                delta = data["choices"][0]["delta"]

                if text := delta.get("reasoning"):
                    if last_section != "reasoning":
                        print("\nReasoning:")
                        last_section = "reasoning"
                    print(f"{GRAY}{text}{RESET}", end="", flush=True)
                    reasoning += text

                if text:= delta.get("content", ""):
                    if last_section != "content":
                        print("\n\nAssistant:")
                        last_section = "content"
                    print(text, end="", flush=True)
                    content+=text

                for call in delta.get("tool_calls", []):
                    index = call["index"]
                    if index not in tool_calls:
                        tool_calls[index] = {
                            "id":call.get("id"),
                            "type":"function",
                            "function":{
                                "name":"",
                                "arguments": ""
                            }
                        }

                    current = tool_calls[index]

                    if call.get("id"):
                        current["id"] = call["id"]

                    function = call.get("function", {})

                    if function.get("name"):
                        current["function"]["name"] = function["name"]

                    if function.get("arguments"):
                        current["function"]["arguments"] += function["arguments"]

        tool_calls = list(tool_calls.values())

        for call in tool_calls:
            function = call["function"]

            if not call.get("id") or not function.get("name"):
                raise ValueError("Incomplete model tool call")

            if not function.get("arguments"):
                raise ValueError("Missing tool call arguments")

        return reasoning, content, tool_calls, usage

    async def chat(self, session, user_input, tools=None, max_iteration=10):
        async with session.lock:
            tracer = Tracer(session.id)
            await tracer.load()

            turn_id = (
                sum(e["type"] == "user_input" for e in tracer.events) + 1
            )

            tracer.record_user(turn_id, user_input)

            session.messages.append({
                "role": "user",
                "content": user_input
            })

            try:
                for _ in range(max_iteration):
                    payload = {
                        "model": self.model,
                        "messages": session.messages,
                        "stream": True,
                        "stream_options": {"include_usage": True}
                    }

                    if tools:
                        payload["tools"] = tools

                    # Model execution
                    start = time.perf_counter()

                    try:
                        reasoning, content, tool_calls, usage = (
                            await self.stream_response(payload)
                        )

                    except httpx.TimeoutException:
                        error_message = "Model request timed out"

                    except httpx.HTTPStatusError as e:
                        error_message = f"Model API returned HTTP {e.response.status_code}"

                    except httpx.RequestError as e:
                        error_message = f"Model connection failed: {e}"

                    except Exception:
                        error_message = "Unexpected model execution failure"
                        logger.exception("Model execution failed")

                    else:
                        error_message = None

                    if error_message:
                        tracer.record_model(
                            turn_id=turn_id,
                            reasoning="",
                            content=None,
                            tool_calls=[],
                            usage={},
                            duration_ms=round(
                                (time.perf_counter() - start) * 1000, 2
                            ),
                            status="error",
                            error_message=error_message
                        )

                        raise RuntimeError(error_message)

                    duration_ms = round(
                        (time.perf_counter() - start) * 1000, 2
                    )

                    # Record model event
                    tracer.record_model(
                        turn_id=turn_id,
                        reasoning=reasoning,
                        content=content or None,
                        tool_calls=tool_calls,
                        usage=usage,
                        duration_ms=duration_ms
                    )

                    assistant_message = {
                        "role": "assistant",
                        "content": content or None
                    }

                    if tool_calls:
                        assistant_message["tool_calls"] = tool_calls

                    session.messages.append(assistant_message)

                    if not tool_calls:
                        return assistant_message

                    # Tool execution
                    
                    for call in tool_calls:
                        name = call["function"]["name"]
                        raw_args = call["function"]["arguments"]

                        try:
                            args = json.loads(raw_args)

                        except json.JSONDecodeError:
                            args = {"raw_arguments": raw_args}

                            result = ToolResult(
                                status="error",
                                error_message="Invalid JSON tool arguments",
                                error_code="INVALID_JSON"
                            )

                            tracer.record_tool(
                                turn_id=turn_id,
                                tool_call_id=call["id"],
                                name=name,
                                arguments=args,
                                result=result,
                                duration_ms=0
                            )

                        else:
                            result = await self.execute_tool(
                                name=name,
                                args=args,
                                tracer=tracer,
                                turn_id=turn_id,
                                tool_call_id=call["id"]
                            )


                        session.messages.append({
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "content": result.model_dump_json()
                        })

                tracer.record_model(
                    turn_id=turn_id,
                    reasoning="",
                    content=None,
                    tool_calls=[],
                    usage={},
                    duration_ms=0,
                    status="error",
                    error_message="Exceeded maximum tool call iterations"
                )

                raise RuntimeError("Exceeded maximum tool call iterations")

            finally:
                await tracer.save()


    async def close(self):
        await self.client.aclose()