import imaplib
from email import message_from_bytes
from email.header import decode_header
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re

class EmailFetchAgent:
    def __init__(self, email_address: str, app_password: str, imap_server: str = "imap.gmail.com"):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = imap_server
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def strip_html_tags(self,html):
        """
        Simpler version with basic cleaning
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        
        # Remove invisible characters
        text = re.sub(r'[\u200b\u200c\u200d\u2007\u2060\ufeff\u00a0]+', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def connect(self) -> None:
        self.connection = imaplib.IMAP4_SSL(self.imap_server)
        self.connection.login(self.email_address, self.app_password)
        self.connection.select("inbox")

    def fetch_latest_emails(self) -> List[Dict[str, str]]:
        assert self.connection is not None, "IMAP connection not established"
        
        status, all_ids = self.connection.search(None, "ALL")
        status, unread_ids = self.connection.search(None, "UNSEEN")
        
        all_id_list = all_ids[0].split()
        unread_id_list = set(unread_ids[0].split())

        latest_ids = all_id_list[-2:]  # or however many you want

        results = []

        for num in latest_ids:
            status, data = self.connection.fetch(num.decode(), "(RFC822)")
            for response in data:
                if isinstance(response, tuple):
                    msg = message_from_bytes(response[1])

                    subject_raw, encoding = decode_header(msg["Subject"])[0]
                    subject = (
                        subject_raw.decode(encoding or "utf-8")
                        if isinstance(subject_raw, bytes)
                        else subject_raw
                    )

                    from_ = msg.get("From", "(Unknown Sender)")
                    body = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_dispo = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_dispo:
                                payload = part.get_payload(decode=True)
                                if isinstance(payload, bytes):
                                    body = payload.decode("utf-8", errors="ignore").strip()
                                break  # prefer plain text, stop after first match

                            elif content_type == "text/html" and not body:
                                payload = part.get_payload(decode=True)
                                if isinstance(payload, bytes):
                                    body = payload.decode("utf-8", errors="ignore").strip()

                    else:
                        payload = msg.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body = payload.decode("utf-8", errors="ignore")

                    is_unread = num in unread_id_list  # ✅ this line added here
                    body = self.strip_html_tags(body)

                    results.append({
                        "from": from_,
                        "subject": subject,
                        "body": body,
                        "unread": is_unread
                    })

        return results


    def disconnect(self) -> None:
        if self.connection:
            self.connection.logout()
