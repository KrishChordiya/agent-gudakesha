import httpx
from tools import execute_tool
import json

class Client:
    def __init__(self, base_url, model, api_key, tool_executor=None):
        self.model = model
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=180
        )
        self.messages=[]
        
        self.tool_executor = tool_executor or execute_tool

    async def execute_tool(self, name, args):
        GRAY = "\033[38;5;245m"
        RESET = "\033[0m"
        print("\n\nTool Call:")
        print(f"{GRAY}{name}:{args}{RESET}")
        return await self.tool_executor(name, args)
        
    async def stream_response(self, payload):
        GRAY = "\033[38;5;245m"
        RESET = "\033[0m"
        content = ""
        tool_calls = {}
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
                delta = data["choices"][0]["delta"]

                if text := delta.get("reasoning"):
                    if last_section != "reasoning":
                        print("\nReasoning:")
                        last_section = "reasoning"
                    print(f"{GRAY}{text}{RESET}", end="", flush=True)

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
                            "tool_id":call["id"],
                            "type":"function",
                            "function":{
                                "name":"",
                                "arguments": ""
                            }
                        }

                    function = call["function"]

                    if "name" in function:
                        tool_calls[index]["function"]["name"] = function["name"]
                    
                    #  Aruguments can come in multiple chunks
                    if "arguments" in function:
                        tool_calls[index]["function"]["arguments"] += function["arguments"]

        reply = {
            "role":"assistant",
            "content":content or None
        }

        if tool_calls:
            reply["tool_calls"] = [tool_calls[i] for i in tool_calls]

        return reply

    async def chat(self, user_input, tools=None, max_iteration=10):
        self.messages.append({
            "role":"user",
            "content": user_input
        })

        for _ in range(max_iteration):
            payload = {
                "model": self.model,
                "messages": self.messages,
                "stream": True
            }

            if tools:
                payload["tools"] = tools

            # Get complete streamed assistant response
            reply = await self.stream_response(payload)

            # Store assistant response
            self.messages.append(reply)

            if not reply.get("tool_calls"):
                return
            
            for call in reply["tool_calls"]:
                function = call["function"]
                name = function["name"]
                args = json.loads(function["arguments"])
                result = await self.execute_tool(name, args)

                self.messages.append({
                    "role":"tool",
                    "tool_call_id": call["tool_id"],
                    "content": result.model_dump_json()
                })

        raise RuntimeError("Exceeded maximum tool call iterations")
    
    def get_messages(self):
        return self.messages

    async def close(self):
        await self.client.aclose()