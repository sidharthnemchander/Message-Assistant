import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from client.menu import show_menu, handle_choice

async def main():
    server_params = StdioServerParameters(
        command="python", args=["-u","mcp_server.py"]
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            running = True
            while running:
                show_menu()
                choice = input("Enter your choice: ").strip()
                running = await handle_choice(choice, session)

if __name__ == "__main__":
    asyncio.run(main())
