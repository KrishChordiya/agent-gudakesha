import os
import asyncio
from dotenv import load_dotenv

from client import Client
from tools import TOOLS
from utils import get_prompt

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
API_KEY=os.getenv("API_KEY")

async def main():
    # Clients
    client = Client(BASE_URL, MODEL, API_KEY)

    client.messages.append({
        "role":"system",
        "content":get_prompt("SOUL.md")
    })

    while True:
        user_input = input("\nUser: ")
        
        if user_input=="/exit":
            await client.close()
            break

        await client.chat(user_input, TOOLS, max_iteration=10)

if __name__=="__main__":
    asyncio.run(main())