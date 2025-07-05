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
        try:
            print("Starting Telegram connection...")
            async with self.app:
                print("Connected to Telegram API successfully!")

                print("Fetching dialogs...")
                dialog_gen = self.app.get_dialogs()  # ❌ NO await here

                print("Got dialogs, processing chats...")
                chat_count = 0

                async for dialog in dialog_gen:
                    if chat_count >= 3:
                        break

                    chat_id = dialog.chat.id
                    chat_name = getattr(dialog.chat, 'title', getattr(dialog.chat, 'first_name', 'Unknown'))
                    print(f"Processing chat {chat_count + 1}: {chat_name}")

                    messages = []
                    history_gen = self.app.get_chat_history(chat_id, limit=3)  # ❌ NO await here

                    msg_count = 0
                    async for msg in history_gen:
                        if msg.text:
                            messages.append(msg.text)
                            msg_count += 1

                    print(f"  - Got {msg_count} messages")
                    self.messages_by_chat[chat_id] = list(reversed(messages))
                    chat_count += 1

                print(f"Completed! Processed {chat_count} chats total")

        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback
            traceback.print_exc()



    def get_all_messages(self):
        return self.messages_by_chat