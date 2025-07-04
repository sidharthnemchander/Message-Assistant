from server.getting_mail import EmailFetchAgent
from server.send_emails import EmailSendAgent
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.environ["EMAIL_ADDRESS"]
PASSWORD = os.environ["EMAIL_PASSWORD"]

class EmailAgent:
    def __init__(self):
        self.name = "email_agent"
        self.agent = EmailFetchAgent(email_address=EMAIL, app_password=PASSWORD)
        self.send_agent = EmailSendAgent(EMAIL, PASSWORD)

    async def fetch_latest_emails(self):
        """Fetch the latest emails from the inbox"""
        self.agent.connect()
        try:
            print("The email_agent.py is working")
            emails = self.agent.fetch_latest_emails()
            return {"emails": emails}
        finally:
            self.agent.disconnect()

    async def handle_task(self, task: str, **kwargs):
        """Handle various email-related tasks"""
        if "latest emails" in task.lower():
            return await self.fetch_latest_emails()
        return {"error": "I don't understand the request."}
    
    async def send_emails(self,sub : str, to : str, body : str):
        try:
            return self.send_agent.send_email(sub,to,body)
        except Exception as e:
            return {"error",str(e)}