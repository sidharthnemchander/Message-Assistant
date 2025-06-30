import imaplib
from email import message_from_bytes
from email.header import decode_header
from typing import List, Dict, Optional


class EmailFetchAgent:
    def __init__(self, email_address: str, app_password: str, imap_server: str = "imap.gmail.com"):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = imap_server
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        self.connection = imaplib.IMAP4_SSL(self.imap_server)
        self.connection.login(self.email_address, self.app_password)
        self.connection.select("inbox")

    def fetch_latest_emails(self) -> List[Dict[str, str]]:
        assert self.connection is not None, "IMAP connection not established"
        status, messages = self.connection.search(None, "ALL")
        email_ids = messages[0].split()
        latest_ids = email_ids[-100:]  # ✅ up to latest 100 emails

        results = []

        for num in latest_ids:
            status, data = self.connection.fetch(num, "(RFC822)")
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
                            if part.get_content_type() == "text/plain":
                                payload = part.get_payload(decode=True)
                                if isinstance(payload, bytes):
                                    body = payload.decode("utf-8", errors="ignore")
                                break
                    else:
                        payload = msg.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body = payload.decode("utf-8", errors="ignore")

                    results.append({
                        "from": from_,
                        "subject": subject,
                        "body": body
                    })

        return results

    def disconnect(self) -> None:
        if self.connection:
            self.connection.logout()
