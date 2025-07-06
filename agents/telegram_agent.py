import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from server.t_get_msgs import TelegramBotServer
from telethon import TelegramClient

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv(find_dotenv())

app_id = os.environ["TELEGRAM_APP_API"]
app_hash_id = os.environ["TELEGRAM_APP_HASH"]
phone_number = os.environ["PHONE_NUMBER"]

class TelegramAgent:
    def __init__(self):
        self.get_agent = TelegramBotServer(app_id, app_hash_id)

    async def fetch_messages(self):
        result = await self.get_agent.fetch_messages()
        if result:
            return {str(chat_id): msgs for chat_id, msgs in result.items()}
        else:
            return {"AGENT" : "Nothing is fetched from telegram_agent.py"}
        
    async def send_message(self, to: str, body: str):
        result = await asyncio.wait_for(
            self._send_message_internal(to, body),
            timeout=30.0
        )
        return result
    
    async def _send_message_internal(self, to: str, body: str):
        async with TelegramClient("send_message_session", int(app_id), app_hash_id) as client:
            sent_message = await client.send_message(to, body)
            return {"status": "success", "message_id": sent_message.id}