from dotenv import load_dotenv
import os
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from typing import cast

env_path = Path(__file__).resolve().parent.parent / "agents" / ".env"
load_dotenv(dotenv_path = env_path)

email = cast(str,os.getenv("EMAIL_ADDRESS"))
password = cast(str,os.getenv("EMAIL_PASSWORD"))

class EmailSendAgent:
    def __init__(self,smtp_server: str = "smtp.gmail.com"):
        self.email_address = email
        self.app_password = password
        self.smtp_server = smtp_server
        self.port = 587
        
    def send_email(self, subject : str , To : str, Body : str):
        message = MIMEText(Body)
        message["Subject"] = subject
        message["From"] = self.email_address
        message["To"] = To
        message.attach(MIMEText(Body,'plain'))

        try:
            # Connect to the SMTP server
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email_address, self.app_password)
                server.send_message(message)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")