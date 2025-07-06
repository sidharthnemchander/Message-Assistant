import asyncio
from agents.telegram_agent import TelegramAgent

async def test_direct():
    telegram_agent = TelegramAgent()
    result = await telegram_agent.fetch_messages()
    
    # if result:
    #     for chat_id, messages in result.items():
    #         print(f"Chat {chat_id}: {len(messages)} messages")
    #         for i, msg in enumerate(messages):
    #             print(f"  Message {i+1}: {msg[:50]}...")  # First 50 chars
    # else:
    #     print("No messages returned!")
    return result

if __name__ == "__main__":
    asyncio.run(test_direct())