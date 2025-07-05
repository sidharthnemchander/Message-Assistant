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
        return self.get_agent.run()