from pyrogram.client import Client
from collections import defaultdict

SESSION_NAME = 'telegram_session'

class TelegramBotServer:
    def __init__(self, API_ID : str, API_HASH: str):
        self.app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
        self.messages_by_chat = defaultdict(list)

    async def fetch_messages(self):
        async with self.app:
            dialog_gen = self.app.get_dialogs()
            chat_count = 0
            
            async for dialog in dialog_gen: # type: ignore (This show a coroutine type error but its working tho)
                if chat_count >= 3:
                    print("TelegramBotServer: Reached limit of 3 chats")
                    break

                chat_id = dialog.chat.id
                chat_name = dialog.chat.title
                messages = []
                history_gen = self.app.get_chat_history(chat_id, limit=3)
                msg_count = 0
                async for msg in history_gen: # type: ignore (This show a coroutine type error but its working tho)
                    if msg.text:
                        messages.append(msg.text)
                        msg_count += 1
                self.messages_by_chat[chat_name] = list(reversed(messages))

                chat_count += 1
        result = self.messages_by_chat
        return result

    def get_all_messages(self):
        return self.messages_by_chat