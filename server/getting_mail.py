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
        self.connection.select('"[Gmail]/All Mail"')

    def fetch_latest_emails(self) -> List[Dict[str, str]]:
        assert self.connection is not None, "IMAP connection not established"
        
        status, all_ids = self.connection.search(None, "ALL")
        status, unread_ids = self.connection.search(None, "UNSEEN")
        
        all_id_list = all_ids[0].split()
        unread_id_list = set(unread_ids[0].split())

        print(f"Debug: Total emails found: {len(all_id_list)}")
        print(f"Debug: Email IDs: {[id.decode() for id in all_id_list[-15:]]}")  # Show last 15 IDs
        
        latest_ids = all_id_list[-10:]
        print(f"Debug: Attempting to fetch {len(latest_ids)} emails")

        results = []

        for i, num in enumerate(latest_ids):
            try:
                print(f"Debug: Processing email {i+1}/{len(latest_ids)} (ID: {num.decode()})")
                status, data = self.connection.fetch(num.decode(), "(RFC822)")
                
                for response in data:
                    if isinstance(response, tuple):
                        msg = message_from_bytes(response[1])

                        # Handle subject more safely
                        subject = "(No Subject)"
                        if msg["Subject"]:
                            try:
                                subject_parts = decode_header(msg["Subject"])
                                if subject_parts:
                                    subject_raw, encoding = subject_parts[0]
                                    subject = (
                                        subject_raw.decode(encoding or "utf-8")
                                        if isinstance(subject_raw, bytes)
                                        else subject_raw or "(No Subject)"
                                    )
                            except Exception as e:
                                print(f"Debug: Subject decode error: {e}")
                                subject = str(msg["Subject"])[:100]  # Truncate if too long

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

                        is_unread = num in unread_id_list
                        body = self.strip_html_tags(body)

                        results.append({
                            "from": from_,
                            "subject": subject,
                            "body": body,
                            "unread": is_unread
                        })
                        print(f"Debug: Successfully processed email: {subject}")
                        
            except Exception as e:
                print(f"Debug: Failed to process email {num.decode()}: {e}")

        print(f"Debug: Successfully processed {len(results)} out of {len(latest_ids)} emails")
        return results


    def disconnect(self) -> None:
        if self.connection:
            self.connection.logout()
