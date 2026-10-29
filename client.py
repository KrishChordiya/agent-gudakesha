import httpx
from tools import execute_tool

class Client:
    def __init__(self, base_url, model, api_key):
        self.model = model
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=180
        )
    
    def execute_tool(self, name, args):
        print(f"Tool {name} called with {args}")
        return execute_tool(name, args)

    def chat(self, messages, tools=None):
        payload = {
            "model":self.model,
            "messages" : messages
        }

        if tools:
            payload["tools"] = tools
        
        response = self.client.post(
            "chat/completions",
            json=payload
        )

        response.raise_for_status()
        return response.json()["choices"][0]["message"]
    
    def close(self):
        self.client.close()