import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSendAgent:
    def __init__(self,send_add : str, mail_pass : str, smtp_server: str = "smtp.gmail.com"):
        self.email_address = send_add
        self.app_password = mail_pass
        self.smtp_server = smtp_server
        self.port = 587
        
    def send_email(self, subject : str , To : str, Body : str):
        message = MIMEMultipart()
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