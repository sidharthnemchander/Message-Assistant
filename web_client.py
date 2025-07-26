import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import uvicorn

app = FastAPI(title="Email and Telegram Assistant")

async def call_mcp_server(tool_name: str):
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],  # Fixed: direct script execution
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
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 40px;
      }
      button {
        padding: 10px 20px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        margin-right: 10px;
      }
      button:hover {
        background: #0056b3;
      }
      #GotMail,
      #GotCategory {
        margin-top: 20px;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 5px;
      }
    </style>
  </head>
  <body>
    <h1>Email and Telegram Assistant</h1>

    <button onclick="getMails()">Get Emails</button>
    <button onclick="getCategory()">Get Categories</button>

    <div id="GotMail">Click "Get Emails" button to sync emails</div>
    <div id="GotCategory">
      Click "Get Categories" button to categorize emails
    </div>

    <script>
      const GotMail = document.getElementById("GotMail");
      const categories = document.getElementById("GotCategory");

      async function getMails() {
        GotMail.textContent = "Loading...";

        try {
          const response = await fetch("/getMail", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
          });

          const res = await response.json();

          if (response.ok) {
            GotMail.innerHTML = `<pre>${JSON.stringify(res, null, 2)}</pre>`;
          } else {
            GotMail.textContent = `Error: ${
              res.detail || "Failed to fetch emails"
            }`;
          }
        } catch (error) {
          GotMail.textContent = "Error: " + error.message;
        }
      }

      async function getCategory() {
        categories.textContent = "Please wait while we are sorting...";

        try {
          const response = await fetch("/GetCategories", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
          });
          const res = await response.json();
          if (response.ok) {
            categories.innerHTML = `<pre>${JSON.stringify(res, null, 2)}</pre>`;
          } else {
            categories.textContent =
              "ERROR: " + (res.detail || "Failed to categorize");
          }
        } catch (error) {
          categories.textContent = "ERROR: " + error.message;
        }
      }
    </script>
  </body>
</html>

    """
    return html_content

@app.post("/getMail")
async def getting_mail():
    """Getting the mail from server tool"""
    try:
        answer = await call_mcp_server("get_latest_emails")
        return {"success": True, "data": "We can succesfully synced your emails"}
    except Exception as e:
        print(f"Error getting mail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/GetCategories")
async def getting_categories():
    """Getting the categories from server tool"""
    try :
        answer = await call_mcp_server("categorize_all_emails")
        return answer
    except Exception as e:
        print(f"Error in categorizing through tool {e}")
        raise HTTPException(status_code = 500,detail = str(e))

if __name__ == "__main__":
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="127.0.0.1", port=8000)