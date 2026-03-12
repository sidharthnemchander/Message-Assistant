import json
from embed import get_embedding

def add_msg(db_conn, msg_id, src, sndr, ts, is_read, txt, sub):
    cursor = db_conn.cursor()
    
    cursor.execute(
        "INSERT OR REPLACE INTO metadata (id, source, sender, timestamp, is_read, content, subject) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (msg_id, src, sndr, ts, is_read, txt, sub)
    )
    
    vec = get_embedding(txt)
    
    cursor.execute(
        "INSERT OR REPLACE INTO vectors (id, embedding) VALUES (?, ?)",
        (msg_id, json.dumps(vec))
    )
    
    db_conn.commit()

def ingest_emails(db_conn, emails):
    for idx, e in enumerate(emails):
        msg_id = f"email_{idx}"
        is_read = 0 if e.get("unread") == False else 1
        ts = e.get("date", "")
        txt = e.get("body", "")
        sndr = e.get("from", "unknown")
        sub = e.get("subject", "")
        
        add_msg(db_conn, msg_id, "email", sndr, ts, is_read, txt, sub)

def ingest_telegram(db_conn, tg_data):
    for chat_name, msgs in tg_data.items():
        for idx, msg in enumerate(msgs):
            msg_id = f"tg_{chat_name}_{idx}"
            txt = msg if isinstance(msg, str) else str(msg)
            
            add_msg(db_conn, msg_id, "telegram", chat_name, "", 1, txt,"This is a telegram messages")