import asyncio
from agents.telegram_agent import TelegramAgent

async def test_direct():
    telegram_agent = TelegramAgent()
    result = await telegram_agent.fetch_messages()
    print(result)
    return result

if __name__ == "__main__":
    asyncio.run(test_direct())