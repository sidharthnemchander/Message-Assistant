from mcp.server.fastmcp import FastMCP
from agents.email_agent import EmailAgent
from agents.classifier_agent import ClassifierAgent
import asyncio

# Create FastMCP server
mcp = FastMCP("Email Assistant Server")

# Initialize the email agent
email_agent = EmailAgent()
classifier_agent = ClassifierAgent()

@mcp.tool()
async def get_latest_emails() -> dict:
    """Fetch the latest emails from the inbox"""
    return await email_agent.fetch_latest_emails()

@mcp.tool()
async def handle_email_task(task: str) -> dict:
    """Handle various email-related tasks"""
    return await email_agent.handle_task(task)

@mcp.tool()
async def classify_subject(subject: str) -> str:
    category = classifier_agent.classify_subject(subject)
    return str(category)

if __name__ == "__main__":
    # Run the server
    print("Starting the server")
    mcp.run()