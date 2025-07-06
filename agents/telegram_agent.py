import os
from dotenv import load_dotenv, find_dotenv
from server.t_get_msgs import TelegramBotServer

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv(find_dotenv())

app_id = os.environ["TELEGRAM_APP_API"]
app_hash_id = os.environ["TELEGRAM_APP_HASH"]

class TelegramAgent:
    def __init__(self):
        self.get_agent = TelegramBotServer(app_id, app_hash_id)

    async def fetch_messages(self):
        result = await self.get_agent.fetch_messages()
        if result:
            return {str(chat_id): msgs for chat_id, msgs in result.items()}
        else:
            return {"AGENT" : "Nothing is fetched from telegram_agent.py"}