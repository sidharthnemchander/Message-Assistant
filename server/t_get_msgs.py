import asyncio
from telegram.ext import Application, MessageHandler, filters
from pyrogram.client import Client
from collections import defaultdict

SESSION_NAME = 'telegram_session'

class TelegramBotServer:
    def __init__(self, API_ID : str, API_HASH: str):
        self.app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
        self.messages_by_chat = defaultdict(list)

    async def fetch_messages(self):
        async with self.app:
            # Await the coroutine to get the async generator
            dialogs = await self.app.get_dialogs()
            if dialogs is None:
                print("DIALOGS IS NONE")
                return
            
            async for dialog in dialogs:
                chat_id = dialog.chat.id
                messages = []
                
                # Await the coroutine to get the async generator
                chat_history = await self.app.get_chat_history(chat_id, limit=50)
                if chat_history is not None:
                    async for msg in chat_history:
                        if msg.text:
                            messages.append(msg.text)

                # Now it's safe to reverse because it's a list
                self.messages_by_chat[chat_id] = list(reversed(messages))
    def run(self):
        asyncio.run(self.fetch_messages())

    def get_all_messages(self):
        return self.messages_by_chat