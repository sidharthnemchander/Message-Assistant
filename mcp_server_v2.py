from mcp.server.fastmcp import FastMCP
import json
import sqlite3
import sqlite_vec
from db import init_db
from embed import get_embedding
from agents.LLMchatbot import LLMChatBot
from ingest import ingest_emails, ingest_telegram
from agents.email_agent import EmailAgent
from agents.telegram_agent import TelegramAgent

mcp = FastMCP("Email & Telegram Agent V2")
bot = LLMChatBot()

db_conn, c = init_db("data.db")

@mcp.tool()
async def exact_search(sql_query: str) -> str:
    cursor = db_conn.cursor()
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return json.dumps(rows)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def semantic_search(search_text: str, sql_filter: str = "", limit: int = 5) -> str:
    vector = get_embedding(search_text)
    cursor = db_conn.cursor()
    
    query = """
        SELECT m.source, m.sender, m.timestamp, m.content 
        FROM vectors v
        JOIN metadata m ON v.id = m.id
        WHERE v.embedding MATCH ?
    """
    
    if sql_filter:
        query += f" AND {sql_filter}"
        
    query += " LIMIT ?"
    
    try:
        cursor.execute(query, (json.dumps(vector), limit))
        rows = cursor.fetchall()
        return json.dumps(rows)
    except Exception as e:
        return json.dumps({"error": str(e)})
    
@mcp.tool()
async def chat_about_data(q: str) -> str:
    p = """
    Database Schema:
    Table: metadata
    Columns: id, source, sender, timestamp, is_read, content
    
    Tools Available:
    1. exact_search(sql_query): For math, dates, counts, exact names.
    2. semantic_search(search_text, sql_filter): For meaning, sentiment, topics.
    
    Determine the best tool for the question, execute it, read the returned data, and answer the user directly.
    """
    
    ans = await bot.query_llm(q, p)
    return ans

email_agent = EmailAgent()
telegram_agent = TelegramAgent()

@mcp.tool()
async def get_latest_emails():
    result = await email_agent.fetch_latest_emails() # result = 'emails' : [{from : str , 'subject' : str, 'body' : str, 'unread' : {True / False}]
    
    if "emails" in result:
        ingest_emails(db_conn, result["emails"])
        
    return json.dumps({"status": "success", "count": len(result.get("emails", []))})

@mcp.tool()
async def get_telegram_messages():
    msgs = await telegram_agent.fetch_messages()
    
    ingest_telegram(db_conn, msgs)
    
    return json.dumps({"status": "success", "chats_synced": len(msgs.keys())})

