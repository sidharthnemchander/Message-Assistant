import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from mcp import ClientSession
import uvicorn
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import TextContent
from client import state

app = FastAPI(title="Email and Telegram Assistant")

MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"

async def call_mcp_server(tool_name: str, params = None):
    """Connects to the persistent MCP HTTP server and calls a tool."""
    try:
        # Connects to the server running on port 8001
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write,_):
            async with ClientSession(read, write) as session:
                await session.initialize()
                if params:
                    result = await session.call_tool(tool_name, **params)
                else:
                    result = await session.call_tool(tool_name)
                
                return result.content[0] if result.content else "No result"
    
    except Exception as e:
        print(f"Could not connect to MCP server or call tool: {e}")
        raise HTTPException(status_code=503, detail="MCP server is unavailable.")


@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve a simple HTML interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Email and Telegram DM Unify</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px; }
          button:hover { background: #0056b3; }
          #GotMail, #GotCategory { margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        </style>
      </head>
      <body>
        <h1>Email and Telegram Assistant</h1>
        <button onclick="getMails()">Get Emails</button>
        <button onclick="getCategory()">Get Categories</button>
        <div id="GotMail">Click "Get Emails" button to sync emails</div>
        <div id="GotCategory">Click "Get Categories" button to categorize emails</div>
        <script>
          const GotMail = document.getElementById("GotMail");
          const categories = document.getElementById("GotCategory");

          async function getMails() {
            GotMail.textContent = "Loading...";
            try {
              const response = await fetch("/getMail", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({}) });
              const res = await response.json();
              if (response.ok) {
                GotMail.innerHTML = `<pre>${JSON.stringify(res, null, 2)}</pre>`;
              } else {
                GotMail.textContent = `Error: ${res.detail || "Failed to fetch emails"}`;
              }
            } catch (error) {
              GotMail.textContent = "Error: " + error.message;
            }
          }

          async function getCategory() {
            categories.textContent = "Please wait while we are sorting...";
            try {
              const response = await fetch("/GetCategories", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
              const res = await response.json();
              if (response.ok) {
                categories.innerHTML = `<pre>${JSON.stringify(res, null, 2)}</pre>`;
              } else {
                categories.textContent = "ERROR: " + (res.detail || "Failed to categorize");
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
    """Getting the mail from server tool and storing it in the client's state."""
    try:
        answer = await call_mcp_server("get_latest_emails")
        
        if isinstance(answer, TextContent):
            data = json.loads(answer.text)
            email_list = data.get('emails', [])

            # Clear previous state before syncing new emails
            state.froms.clear()
            state.subjects.clear()
            state.subjects_to_body.clear()
            state.bodys.clear()
            state.unreads.clear()

            for email_obj in email_list:
                state.froms.append(email_obj["from"])
                state.subjects.append(email_obj["subject"])
                state.subjects_to_body[email_obj["subject"]] = email_obj["body"]
                state.bodys.append(email_obj["body"])
                if email_obj.get("unread"):
                    state.unreads.append(email_obj["subject"])
            
            return {"success": True, "data": f"Successfully synced and stored {len(email_list)} emails."}
        else:
            return {"success": False, "data": "Did not receive valid email data from server."}
    
    except HTTPException as e:
        raise e # Re-raise the specific HTTP error from call_mcp_server
    except Exception as e:
        print(f"Error getting mail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/GetCategories")
async def getting_categories():
    """Getting the categories from the server tool."""
    if not state.subjects:
        return {"success": False, "data": "Please sync emails first."}

    try:
        # Make a SINGLE, efficient call to the server tool that does all the work
        answer = await call_mcp_server("categorize_all_emails")

        if isinstance(answer, TextContent) and answer.text.strip().startswith('{'):
            response_data = json.loads(answer.text)
            print("Server categorization summary received.")
            return {"success": True, "data": response_data}
        else:
            # Handle cases where the server returned a plain error message
            error_message = answer.text if isinstance(answer, TextContent) else "Invalid response from server."
            return {"success": False, "data": error_message}

    except HTTPException as e:
        raise e # Re-raise the specific HTTP error from call_mcp_server
    except Exception as e:
        print(f"Error in categorizing through tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting web client on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)