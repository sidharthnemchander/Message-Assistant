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
                # Await the coroutine to get the async generator
                dialogs = await self.app.get_dialogs()
                if dialogs is None:
                    print("DIALOGS IS NONE")
                    return
                
                print("Got dialogs, processing chats...")
                chat_count = 0
                async for dialog in dialogs:
                    if chat_count >= 3:  # Only process 3 chats
                        break
                        
                    chat_id = dialog.chat.id
                    chat_name = getattr(dialog.chat, 'title', getattr(dialog.chat, 'first_name', 'Unknown'))
                    print(f"Processing chat {chat_count + 1}: {chat_name}")
                    
                    messages = []
                    
                    # Await the coroutine to get the async generator
                    chat_history = await self.app.get_chat_history(chat_id, limit=3)  # Only 3 messages
                    if chat_history is not None:
                        msg_count = 0
                        async for msg in chat_history:
                            if msg.text:
                                messages.append(msg.text)
                                msg_count += 1
                        print(f"  - Got {msg_count} messages")

                    # Now it's safe to reverse because it's a list
                    self.messages_by_chat[chat_id] = list(reversed(messages))
                    chat_count += 1
                
                print(f"Completed! Processed {chat_count} chats total")
                
        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback
            traceback.print_exc()
    
    # Remove the sync run() method as it's causing the issue
    # def run(self):
    #     asyncio.run(self.fetch_messages())

    def get_all_messages(self):
        return self.messages_by_chat