import asyncio
from mcp.client import MCPClient

async def main():
    client = MCPClient("Email Assistant Client")
    await client.connect()

    # Call the 'get_latest_emails' tool
    result = await client.call("get_latest_emails")
    print("Fetched Emails:")
    for email in result["emails"]:
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Body: {email['body'][:100]}...\n")  # Preview first 100 chars

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
