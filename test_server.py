import asyncio
import json
from mcp_server_v2 import get_latest_emails, get_telegram_messages, exact_search, semantic_search

async def r():
    # print("running get emails")
    # e = await get_latest_emails()
    # print(e)
    
    # t = await get_telegram_messages()
    # print(t)
    
    q = "SELECT source, sender, timestamp FROM metadata LIMIT 5"
    res1 = await exact_search(q)
    print(json.dumps(json.loads(res1), indent=2))
    
    res2 = await semantic_search("urgent deadline or meeting", "", 2)
    print(json.dumps(json.loads(res2), indent=2))

if __name__ == "__main__":
    asyncio.run(r())