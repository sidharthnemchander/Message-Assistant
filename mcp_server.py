from mcp.server.fastmcp import FastMCP
from agents.email_agent import EmailAgent
import asyncio

# Create FastMCP server
mcp = FastMCP("Email Assistant Server")

# Initialize the email agent
email_agent = EmailAgent()

@mcp.tool()
async def get_latest_emails() -> dict:
    """Fetch the latest emails from the inbox"""
    return await email_agent.fetch_latest_emails()

@mcp.tool()
async def handle_email_task(task: str) -> dict:
    """Handle various email-related tasks"""
    return await email_agent.handle_task(task)

if __name__ == "__main__":
    # Run the server
    print("Starting the server")
    mcp.run()