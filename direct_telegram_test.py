import asyncio
from agents.telegram_agent import TelegramAgent

async def test_direct():
    print("Testing TelegramAgent directly...")
    
    telegram_agent = TelegramAgent()
    
    print("Calling fetch_messages()...")
    result = await telegram_agent.fetch_messages()
    
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    if result:
        print(f"Number of chats: {len(result)}")
        for chat_id, messages in result.items():
            print(f"Chat {chat_id}: {len(messages)} messages")
            for i, msg in enumerate(messages):
                print(f"  Message {i+1}: {msg[:50]}...")  # First 50 chars
    else:
        print("No messages returned!")

if __name__ == "__main__":
    asyncio.run(test_direct())