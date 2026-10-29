import json
from tools import TOOLS
from client import Client
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
API_KEY=os.getenv("API_KEY")

if __name__=="__main__":
    client = Client(BASE_URL, MODEL, API_KEY)
    messages = []
    with open("prompts/SOUL.md", "r") as f:
        messages.append({
            "role":"system",
            "content":f.read()
        })
    
    while True:
        user_input = input("User: ")
        if user_input == "/exit":
            client.close()
            break

        messages.append({
            "role":"user",
            "content":user_input
        })

        # Setting limit for tool iteration
        for _ in range(10):
            reply = client.chat(messages, tools=TOOLS)
            # token details are also shown in these
            if "tool_calls" not in reply:
                messages.append({
                    "role":reply["role"],
                    "content":reply['content']
                })
                print(f"Gudakesha: {reply['content']}")
                break
            else:
                messages.append(reply)
                for call in reply["tool_calls"]:
                    function = call["function"]
                    name = function["name"]
                    args = json.loads(function["arguments"])
                    result = client.execute_tool(name, args)
                    messages.append({
                        "role":"tool", 
                        "tool_call_id":call["id"], 
                        "name": name, 
                        "content":result
                    })

        else:
            print("Error: Maximum tool iteration limit reached") 



