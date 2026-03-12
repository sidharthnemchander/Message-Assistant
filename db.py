import sqlite3
import sqlite_vec

def init_db(db_path="data.db"):
    db_conn = sqlite3.connect(db_path)
    db_conn.enable_load_extension(True)
    sqlite_vec.load(db_conn)
    cursor = db_conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id TEXT PRIMARY KEY,
            source TEXT,
            sender TEXT,
            timestamp TEXT,
            is_read INTEGER,
            content TEXT,
            subject TEXT
        )
    """)
    
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vectors USING vec0(
            id TEXT PRIMARY KEY,
            embedding float[384]
        )
    """)
    
    db_conn.commit()
    return db_conn, cursor