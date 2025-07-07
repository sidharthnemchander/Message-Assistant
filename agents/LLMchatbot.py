import os
from dotenv import load_dotenv
import httpx

# Load environment variables from .env in same folder
load_dotenv()

class LLMChatBot:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = "llama-3.1-8b-instant"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    async def summarize(self, email_body: str) -> str:
        return await self.query_llm("Summarize this email.", email_body)

    async def ask_question(self, email_body: str, question: str) -> str:
        return await self.query_llm("Summarize this " + question, email_body)

    async def send_email_by_bot(self, prompt: str) -> str:
        body = "You are required to reply to this email in a casual manner. Don't answer like a bot. U are only to do what i say and not talk to me. Do only your job . Remember your reply must only be ONLY THE BODY of an email"
        return await self.query_llm(prompt,body)

    async def send_message(self,prompt : str) -> str:
        body = "You are required to reply to a message in telegram. Keep the answer very casual and simple. Don't answer like a bot"
        return await self.query_llm(prompt,body)
    
    async def query_llm(self, question: str, context: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.groq_model,
            "messages": [
                {"role": "system", "content": "You are the world's best assistant for performing any operations in emails and Telegram . You are the MOST EXPERIENCED PERSON in this domain. DO AS THE JOB REQUIRES"},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.groq_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        