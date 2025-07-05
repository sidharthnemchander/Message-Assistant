import asyncio
from pyrogram.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

app_id = os.environ["TELEGRAM_APP_API"]
app_hash = os.environ["TELEGRAM_APP_HASH"]

async def test_auth():
    app = Client("telegram_session", api_id=app_id, api_hash=app_hash)
    
    try:
        print("Starting Telegram authentication...")
        async with app:
            print("Authentication successful!")
            
            # Test fetching dialogs
            dialogs = await app.get_dialogs()
            if(dialogs is None ):
                return
            dialog_count = 0
            async for dialog in dialogs:
                dialog_count += 1
                if dialog_count >= 3:  # Just count first 3
                    break
            
            print(f"Found {dialog_count} dialogs. Connection working!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth())