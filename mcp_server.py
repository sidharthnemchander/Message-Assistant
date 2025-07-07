from mcp.server.fastmcp import FastMCP
from agents.email_agent import EmailAgent
from agents.classifier_agent import ClassifierAgent
from agents.LLMchatbot import LLMChatBot
from agents.telegram_agent import TelegramAgent
import json

# Create FastMCP server
titlestr = "Email & Telegram Assistant Server"
mcp = FastMCP(titlestr)

# Initialize agents
email_agent = EmailAgent()
classifier_agent = ClassifierAgent()
bot = LLMChatBot()
telegram_bot = TelegramAgent()


@mcp.tool()
async def get_latest_emails():
    return await email_agent.fetch_latest_emails()

@mcp.tool()
async def handle_email_task(task: str) -> dict:
    return await email_agent.handle_task(task)

@mcp.tool()
async def classify_subject(subject: str) -> str:
    return classifier_agent.classify_subject(subject)

@mcp.tool()
async def summarize(body: str) -> str:
    return await bot.summarize(body)

@mcp.tool()
async def send_emails(subject: str, to: str, body: str):
    return await email_agent.send_emails(subject, to, body)

@mcp.tool()
async def send_mail_by_Groq(prompt: str) -> str:
    return await bot.send_email_by_bot(prompt)

@mcp.tool()
async def get_telegram_messages():
    msgs = await telegram_bot.fetch_messages()
    serialized = json.dumps(msgs)
    return serialized

@mcp.tool()
async def send_telegram_messages(to: str, body: str):
    result = await telegram_bot.send_message(to, body)
    return result

@mcp.tool()
async def message_groq(prompt : str) -> str:
    result = await bot.send_message(prompt)
    return result
if __name__ == "__main__":
    print("Starting the server")
    mcp.run()
