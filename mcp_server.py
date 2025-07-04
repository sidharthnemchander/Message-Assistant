from mcp.server.fastmcp import FastMCP
from agents.email_agent import EmailAgent
from agents.classifier_agent import ClassifierAgent
from agents.LLMchatbot import LLMChatBot
import asyncio

# Create FastMCP server
mcp = FastMCP("Email Assistant Server")

# Initialize the email agent
email_agent = EmailAgent()
classifier_agent = ClassifierAgent()
bot = LLMChatBot()

@mcp.tool()
async def get_latest_emails() -> dict:
    """Fetch the latest emails from the inbox"""
    print("The mcp_server.py is running")
    return await email_agent.fetch_latest_emails()

@mcp.tool()
async def handle_email_task(task: str) -> dict:
    """Handle various email-related tasks"""
    return await email_agent.handle_task(task)

@mcp.tool()
async def classify_subject(subject: str) -> str:
    print("The mcp_server.py is running")
    category = classifier_agent.classify_subject(subject)
    return str(category)

@mcp.tool()
async def summarize(body : str) -> str:
    """Summarize the content through Groq"""
    summarize_content = await bot.summarize(body)
    return str(summarize_content)

@mcp.tool()
async def send_emails(subject : str, to : str, body : str):
    """Sending an email through send_emails.py"""
    return await email_agent.send_emails(subject,to,body)

if __name__ == "__main__":
    # Run the server
    print("Starting the server")
    mcp.run()