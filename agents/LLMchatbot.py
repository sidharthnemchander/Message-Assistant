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
        return await self.query_llm(question, email_body)

    async def send_email(self, recipient: str, subject: str, body: str) -> str:
        # Placeholder implementation
        return f"Email sent to {recipient} with subject '{subject}'."

    async def query_llm(self, question: str, context: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.groq_model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that understands and summarizes emails. Make your answers precise and don't leave any important points. Use the best structure u find appropriate to answer"},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.groq_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        