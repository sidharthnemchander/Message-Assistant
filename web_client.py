import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import uvicorn

app = FastAPI(title="Email and Telegram Assistant")

async def call_mcp_server(tool_name : str):
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server"],
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name)
                return result.content[0] if result.content else "No result"
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve a simple HTML interface."""

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email and Telegram DM Unify</title>
    </head>
    <body>
        <h1>Getting Email</h1>

        <form id="emailForm">
            <button type="submit">Get Emails</button>
            <div id="GotMail">Get Emails button to sync emails</div>
        </form>

        <script>
            const GotMail = document.getElementById('GotMail');

            document.getElementById('emailForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                try {
                    const response = await fetch('/search', {
                        method: "POST",
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({}) // Replace with actual data if needed
                    });

                    const res = await response.json();

                    if (res.success) {
                        GotMail.textContent = JSON.stringify(res);
                    } else {
                        GotMail.textContent = "Failed to fetch emails.";
                    }
                } catch (error) {
                    GotMail.textContent = "Error: " + error.message;
                }
            });
        </script>
    </body>
    </html>
        
        """
@app.post("/getMail")
async def getting_mail():
    """Getting the mail from server tool"""
    try:
        answer = await call_mcp_server("get_latest_emails")
        return answer
    except Exception as e:
        print(e)

if __name__ == "__main__":
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="127.0.0.1", port=8000)