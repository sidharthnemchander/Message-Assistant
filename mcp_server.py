from mcp.server.fastmcp import FastMCP
from agents.email_agent import EmailAgent
from agents.classifier_agent import ClassifierAgent
from agents.LLMchatbot import LLMChatBot
from agents.telegram_agent import TelegramAgent
import json
import uvicorn

# Create FastMCP server
titlestr = "Email & Telegram Assistant Server"
mcp = FastMCP(titlestr)

# Initialize agents
email_agent = EmailAgent()
classifier_agent = ClassifierAgent()
bot = LLMChatBot()
telegram_bot = TelegramAgent()

# Global state storage in server
class ServerState:
    def __init__(self):
        self.emails = []
        self.categorized_emails = {}
        self.froms = []
        self.subjects = []
        self.subjects_to_body = {}
        self.bodys = []
        self.unreads = []
        self.name_message = {}
        self.t_names = []
        self.last_updated = None
    
    def update_emails(self, email_data):
        """Update email state"""
        self.emails = email_data
        self.froms = [email['from'] for email in email_data]
        self.subjects = [email['subject'] for email in email_data]
        self.subjects_to_body = {email['subject']: email['body'] for email in email_data}
        self.bodys = [email['body'] for email in email_data]
        self.unreads = [email['subject'] for email in email_data if email.get('unread')]
        import datetime
        self.last_updated = datetime.datetime.now().isoformat()
    
    def update_categories(self, categories):
        """Update categorized emails"""
        self.categorized_emails = categories
    
    def update_telegram(self, name_message, t_names):
        """Update telegram data"""
        self.name_message = name_message
        self.t_names = t_names

# Global server state
server_state = ServerState()
def get_email_resources():
    """Generate email resources dynamically"""
    resources = []
    
    # Email summary resource
    if server_state.subjects:
        summary = {
            "total_emails": len(server_state.subjects),
            "unread_count": len(server_state.unreads),
            "senders": server_state.froms[:20],  # Limit to prevent size issues
            "recent_subjects": server_state.subjects[:20],
            "categories": list(server_state.categorized_emails.keys()) if server_state.categorized_emails else [],
            "last_updated": server_state.last_updated
        }
        
        resources.append({
            "uri": "email://summary",
            "name": "Email Summary",
            "mimeType": "application/json",
            "text": json.dumps(summary, indent=2)
        })
    
    # Category-wise resources (split to avoid large payloads)
    if server_state.categorized_emails:
        for category, subjects in server_state.categorized_emails.items():
            category_data = []
            for subject in subjects[:10]:  # Limit emails per category
                email_info = {
                    "subject": subject,
                    "body_preview": server_state.subjects_to_body.get(subject, "")[:300],  # Truncated body
                    "is_unread": subject in server_state.unreads,
                    "sender": next((sender for sender, subj in zip(server_state.froms, server_state.subjects) if subj == subject), "Unknown")
                }
                category_data.append(email_info)
            
            resources.append({
                "uri": f"email://category/{category.lower().replace(' ', '_')}",
                "name": f"Emails - {category}",
                "mimeType": "application/json", 
                "text": json.dumps({
                    "category": category,
                    "count": len(subjects),
                    "emails": category_data
                }, indent=2)
            })
    
    # Unread emails resource
    if server_state.unreads:
        unread_data = []
        for subject in server_state.unreads[:10]:  # Limit unread emails
            unread_info = {
                "subject": subject,
                "body_preview": server_state.subjects_to_body.get(subject, "")[:300],
                "sender": next((sender for sender, subj in zip(server_state.froms, server_state.subjects) if subj == subject), "Unknown")
            }
            unread_data.append(unread_info)
        
        resources.append({
            "uri": "email://unread",
            "name": "Unread Emails",
            "mimeType": "application/json",
            "text": json.dumps({
                "unread_count": len(server_state.unreads),
                "unread_emails": unread_data
            }, indent=2)
        })
    
    return resources

def get_telegram_resources():
    """Generate telegram resources dynamically"""
    resources = []
    
    if server_state.t_names:
        # Telegram summary
        summary = {
            "total_chats": len(server_state.t_names),
            "chat_names": server_state.t_names,
            "message_counts": {name: len(messages) for name, messages in server_state.name_message.items()}
        }
        
        resources.append({
            "uri": "telegram://summary",
            "name": "Telegram Summary",
            "mimeType": "application/json",
            "text": json.dumps(summary, indent=2)
        })
        
        # Individual chat resources (limited)
        for chat_name in server_state.t_names[:5]:  # Limit number of chats
            messages = server_state.name_message.get(chat_name, [])
            chat_data = {
                "chat_name": chat_name,
                "message_count": len(messages),
                "recent_messages": messages[-10:] if len(messages) > 10 else messages  # Last 10 messages
            }
            
            resources.append({
                "uri": f"telegram://chat/{chat_name.lower().replace(' ', '_')}",
                "name": f"Chat - {chat_name}",
                "mimeType": "application/json",
                "text": json.dumps(chat_data, indent=2)
            })
    
    return resources

@mcp.resource("email://{uri}")
async def get_email_resource(uri: str):
    """Dynamic email resources"""
    email_resources = get_email_resources()
    
    for resource in email_resources:
        if resource["uri"] == uri:
            return resource
    
    return {
        "uri": uri,
        "name": "Email Resource Not Found",
        "mimeType": "text/plain",
        "text": "No email data available. Please fetch emails first."
    }

@mcp.resource("telegram://{uri}")
async def get_telegram_resource(uri: str):
    """Dynamic telegram resources"""
    telegram_resources = get_telegram_resources()
    
    for resource in telegram_resources:
        if resource["uri"] == uri:
            return resource
    
    return {
        "uri": uri,
        "name": "Telegram Resource Not Found", 
        "mimeType": "text/plain",
        "text": "No telegram data available. Please sync messages first."
    }

@mcp.tool()
async def list_available_resources() -> str:
    """List all currently available resources"""
    email_resources = get_email_resources()
    telegram_resources = get_telegram_resources()
    
    all_resources = email_resources + telegram_resources
    
    if not all_resources:
        return "No resources available. Please fetch emails and sync telegram messages first."
    
    resource_list = []
    for resource in all_resources:
        resource_list.append({
            "uri": resource["uri"],
            "name": resource["name"],
            "type": "Email" if resource["uri"].startswith("email://") else "Telegram"
        })
    
    return json.dumps({"available_resources": resource_list}, indent=2)

@mcp.tool()
async def get_latest_emails():
    result = await email_agent.fetch_latest_emails()
    
    if "emails" in result:
        server_state.update_emails(result["emails"])
    return result

@mcp.tool()
async def handle_email_task(task: str) -> dict:
    return await email_agent.handle_task(task)

@mcp.tool()
async def classify_subject(subject: str) -> str:
    try:
        return classifier_agent.classify_subject(subject)
    except Exception as e:
        return f"agent failed for the subject {subject} : {e}"

@mcp.tool()
async def summarize(body: str) -> str:
    try:
        # This is the line that is likely failing.
        summary_text = await bot.summarize(body[0:100])
        return summary_text
    except Exception as e:
        # Instead of crashing, we catch the error from the agent.
        print(f"--- ERROR IN SUMMARIZE TOOL ---")
        print(f"An exception occurred in the LLMChatBot agent: {e}")
        print(f"--- END OF ERROR ---")
        # And return a helpful error message to the user.
        return f"The summarizer agent failed. Please check the mcp_server console for details. Error: {e}"

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
    server_state.update_telegram(msgs, list(msgs.keys()))
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
async def categorize_all_emails() -> str:
    """Categorize all emails and update server state"""
    if not server_state.subjects:
        return "No emails to categorize. Please fetch emails first."
    
    categorized = {}
    for subject in server_state.subjects:
        category = classifier_agent.classify_subject(subject)
        if not category or category.strip() == "":
            category = "Others"
        categorized.setdefault(category, []).append(subject)
    
    # Update server state
    server_state.update_categories(categorized)
    
    return json.dumps({
        "message": "Emails categorized successfully",
        "categories": categorized
    }, indent=2)

#  ── Function definitions for ChatCompletion ──
functions = [
  {
    "name": "get_email_resource",
    "description": "Fetch email://<uri> (small JSON)",
    "parameters": {
      "type": "object",
      "properties": {
        "uri": {"type": "string"}
      },
      "required": ["uri"]
    }
  },
  {
    "name": "get_telegram_resource",
    "description": "Fetch telegram://<uri> (small JSON)",
    "parameters": {
      "type": "object",
      "properties": {
        "uri": {"type": "string"}
      },
      "required": ["uri"]
    }
  }
]
 

@mcp.tool()
async def chat_about_data(question: str) -> str:
    """Ask questions about your email and telegram data. The LLM will use available resources."""
    if not server_state.subjects and not server_state.t_names:
        return "No data available to chat about. Please fetch emails and sync telegram messages first."
    
    # Pre-fetch relevant data based on question keywords
    data_context = ""
    question_lower = question.lower()
    
    # Always include email summary if emails exist
    if server_state.subjects:
        email_summary = await get_email_resource("email://summary")
        data_context += f"EMAIL SUMMARY:\n{email_summary['text']}\n\n"
        
        # Include unread emails if question mentions unread/important
        if "unread" in question_lower or "important" in question_lower:
            if server_state.unreads:
                unread_data = await get_email_resource("email://unread")
                data_context += f"UNREAD EMAILS:\n{unread_data['text']}\n\n"
        
        # Include ALL category data if question asks for categorized emails or all emails
        if server_state.categorized_emails and ("categor" in question_lower or "all" in question_lower or "show" in question_lower):
            for category in server_state.categorized_emails.keys():
                category_uri = f"email://category/{category.lower().replace(' ', '_').replace('/', '_')}"
                try:
                    category_data = await get_email_resource(category_uri)
                    data_context += f"CATEGORY - {category.upper()}:\n{category_data['text']}\n\n"
                except:
                    continue
        
        # Include specific category data if mentioned
        elif server_state.categorized_emails:
            for category in server_state.categorized_emails.keys():
                if category.lower() in question_lower or any(word in question_lower for word in category.lower().split()):
                    category_uri = f"email://category/{category.lower().replace(' ', '_').replace('/', '_')}"
                    try:
                        category_data = await get_email_resource(category_uri)
                        data_context += f"CATEGORY - {category.upper()}:\n{category_data['text']}\n\n"
                    except:
                        continue
    
    # Include telegram data if question mentions telegram/chat
    if server_state.t_names:
        telegram_summary = await get_telegram_resource("telegram://summary")
        data_context += f"TELEGRAM SUMMARY:\n{telegram_summary['text']}\n\n"
    
    system_prompt = f"""You are an intelligent email and telegram assistant. 
    Here is the current data for the user:

    {data_context}
    
    Instructions:
    - Answer the user's question accurately using ONLY the data provided above
    - Provide exact numbers, counts, and details from the data
    - If asked for specific category emails, list them with subjects and details
    - If asked for categorized emails, organize them clearly by category
    - Be direct and comprehensive in your response
    - Format your response clearly with proper headings and bullet points
    - Don't mention functions or resources - just provide the information directly"""
    
    return await bot.query_llm(question, system_prompt)

app = mcp.streamable_http_app

if __name__ == "__main__":
    print("Starting MCP server on http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
    #completed