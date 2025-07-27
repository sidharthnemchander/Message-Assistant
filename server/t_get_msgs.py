# t_get_msgs.py

from pyrogram.client import Client
from collections import defaultdict

SESSION_NAME = 'telegram_session'

class TelegramBotServer:
    def __init__(self, API_ID: str, API_HASH: str):
        self.app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
        self.messages_by_chat = defaultdict(list)
        # The self._is_connected flag is no longer needed.

    async def connect(self):
        """Connects the client if it's not already connected."""
        # Use the client's built-in property for a reliable check.
        if not self.app.is_connected:
            await self.app.start()
            print("TelegramBotServer: Client connected successfully.")

    async def disconnect(self):
        """Disconnects the client if it's connected."""
        if self.app.is_connected:
            await self.app.stop()
            print("TelegramBotServer: Client disconnected.")

    async def fetch_messages(self):
        """
        Fetches the latest messages from the top 5 chats.
        It ensures a connection is active before fetching.
        """
        await self.connect()

        dialog_gen = self.app.get_dialogs()
        chat_count = 0
        
        latest_messages = defaultdict(list)

        async for dialog in dialog_gen:
            if chat_count >= 5:
                break
            
            chat_id = dialog.chat.id
            chat_name = dialog.chat.title or dialog.chat.first_name or "Unknown"
            messages = []
            history_gen = self.app.get_chat_history(chat_id, limit=3)

            async for msg in history_gen:
                if msg.text:
                    messages.append(msg.text)
            
            latest_messages[chat_name] = list(reversed(messages))
            chat_count += 1
        
        self.messages_by_chat = latest_messages
        return self.messages_by_chat

    def get_all_messages(self):
        return self.messages_by_chat