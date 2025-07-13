from mcp.server.fastmcp import FastMCP
from agents.email_agent import EmailAgent
from agents.classifier_agent import ClassifierAgent
from agents.LLMchatbot import LLMChatBot
from agents.telegram_agent import TelegramAgent
import json
from client import state

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

@mcp.resource("emails://current")
async def get_current_emails():
    """Current email state including subjects, senders, and bodies"""
    return {
        "subjects": state.subjects,
        "froms": state.froms,
        "bodies": state.bodys,
        "unread_subjects": state.unreads,
        "total_emails": len(state.subjects)
    }

@mcp.resource("emails://categories")
async def get_email_categories():
    """Categorized emails with counts"""
    if not state.categorized_emails:
        return {"message": "No emails have been categorized yet"}
    
    categories_with_counts = {}
    for category, subjects in state.categorized_emails.items():
        categories_with_counts[category] = {
            "count": len(subjects),
            "subjects": subjects
        }
    
    return categories_with_counts

@mcp.resource("emails://content")
async def get_email_content():
    """Full email content mapping subjects to bodies"""
    return {
        "subject_to_body": state.subjects_to_body,
        "available_subjects": list(state.subjects_to_body.keys())
    }

@mcp.resource("telegram://messages")
async def get_telegram_state():
    """Current Telegram message state"""
    return {
        "chat_names": state.t_names,
        "name_to_messages": state.name_message,
        "total_chats": len(state.t_names)
    }

@mcp.tool()
async def query_email_state(query_type: str = "all") -> dict:
    """
    Query the current email state
    query_type options: 'all', 'subjects', 'categories', 'unread', 'senders'
    """
    if query_type == "all":
        return {
            "subjects": state.subjects,
            "categories": state.categorized_emails,
            "unread": state.unreads,
            "senders": state.froms,
            "total_emails": len(state.subjects)
        }
    elif query_type == "subjects":
        return {"subjects": state.subjects}
    elif query_type == "categories":
        return {"categories": state.categorized_emails}
    elif query_type == "unread":
        return {"unread_subjects": state.unreads}
    elif query_type == "senders":
        return {"senders": state.froms}
    else:
        return {"error": "Invalid query_type"}
    
@mcp.tool()
async def ask_about_emails(question: str) -> str:
    """Ask questions about your emails using AI with full context"""
    
    # Get data from resources (this is how resources are used)
    current_emails = await get_current_emails()
    categories = await get_email_categories() 
    content = await get_email_content()
    
    # Combine all context
    full_context = {
        "current_emails": current_emails,
        "categories": categories,
        "content": content
    }
    
    return await bot.query_with_email_context(question, full_context)

if __name__ == "__main__":
    print("Starting the server")
    mcp.run()