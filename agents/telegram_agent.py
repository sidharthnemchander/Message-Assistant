from server.t_get_msgs import TelegramBotServer
from dotenv import load_dotenv
import os

load_dotenv()

app_id = os.environ["TELEGRAM_APP_API"]
app_hash_id = os.environ["TELEGRAM_APP_HASH"]

class TelegramAgent:
    def __init__(self):
        self.name = "telegram_agent"
        self.get_agent = TelegramBotServer(app_id,app_hash_id)
    
    async def fetch_messages(self):
        print("TelegramAgent: Starting fetch_messages...")
        try:
            # Call the async method directly instead of the sync wrapper
            await self.get_agent.fetch_messages()
            messages = self.get_agent.get_all_messages()
            print(f"TelegramAgent: Retrieved {len(messages)} chats")
            print(f"TelegramAgent: Messages data: {messages}")
            return messages
        except Exception as e:
            print(f"TelegramAgent: Error occurred: {e}")
            import traceback
            traceback.print_exc()
            return {}