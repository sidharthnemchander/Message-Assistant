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

@mcp.tool()
async def query_email_state_with_data(state_data: dict, query_type: str = "all") -> dict:
    """
    Query email state with provided data
    query_type options: 'all', 'subjects', 'categories', 'unread', 'senders'
    """
    if query_type == "all":
        return state_data
    elif query_type == "subjects":
        return {"subjects": state_data.get("subjects", [])}
    elif query_type == "categories":
        return {"categories": state_data.get("categories", {})}
    elif query_type == "unread":
        return {"unread_subjects": state_data.get("unread", [])}
    elif query_type == "senders":
        return {"senders": state_data.get("senders", [])}
    else:
        return {"error": "Invalid query_type"}

@mcp.tool()
async def ask_about_emails_with_context(question: str, email_context: dict) -> str:
    """Ask questions about emails with provided context"""
    return await bot.query_with_email_context(question, email_context)

@mcp.resource("emails://help")
async def get_email_help():
    """Help information for email resources"""
    return {
        "message": "Email state is managed by the client. Use tools with context parameters.",
        "available_tools": [
            "query_email_state_with_data",
            "ask_about_emails_with_context"
        ],
        "note": "State data must be passed as parameters to tools"
    }

if __name__ == "__main__":
    print("Starting the server")
    mcp.run()