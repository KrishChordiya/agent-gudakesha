import json
import os
from dotenv import load_dotenv

from client import Client
from tools import TOOLS
from utils import get_prompt

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
API_KEY=os.getenv("API_KEY")

if __name__=="__main__":
    # Clients
    client = Client(BASE_URL, MODEL, API_KEY)

    client.messages.append({
        "role":"system",
        "content":get_prompt("SOUL.md")
    })

    while True:
        user_input = input("\nUser: ")
        
        if user_input=="/exit":
            client.close()
            break

        client.chat(user_input, TOOLS, max_iteration=10)