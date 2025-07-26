import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from mcp import ClientSession
import uvicorn
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import TextContent
from client import state
from pydantic import BaseModel

app = FastAPI(title="Email and Telegram Assistant")

MCP_SERVER_URL = "http://127.0.0.1:8001/mcp"

class SubjectRequest(BaseModel):
    subject: str

async def call_mcp_server(tool_name: str, params = None):
    """Connects to the persistent MCP HTTP server and calls a tool."""
    try:
        # Connects to the server running on port 8001
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write,_):
            async with ClientSession(read, write) as session:
                await session.initialize()
                if params:
                    print(f"THIS IS GOING TO WORK with {params}")
                    result = await session.call_tool(tool_name, **params)
                    print("THIS HAS WORKED")
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
    <button onclick="checkCategories()">Check Categories</button>
    <div id="CheckCategory">Click Check Categories Please</div>

    <script>
      const GotMail = document.getElementById("GotMail");
      const categories = document.getElementById("GotCategory");
      const checkCategoryDiv = document.getElementById("CheckCategory");

      let clientState = {
        subjectsToBody: {},
        categorizedEmails: {},
      };
      async function getMails() {
        GotMail.textContent = "Loading...";
        try {
          const response = await fetch("/getMail", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
          });
          const res = await response.json();
          if (response.ok) {
            clientState.subjectsToBody = res["Subject-to-body"] || {}; 
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
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
          });
          const res = await response.json();
          if (response.ok) {
            clientState.categorizedEmails = res.data.categories || {};
            categories.innerHTML = `<pre>${JSON.stringify(res, null, 2)}</pre>`;
          } else {
            categories.textContent =
              "ERROR: " + (res.detail || "Failed to categorize");
          }
        } catch (error) {
          categories.textContent = "ERROR: " + error.message;
        }
      }
      async function checkCategories() {
        checkCategoryDiv.textContent = "Fetching category data...";
        try {
          const response = await fetch("/checkCategoryData", {
            method: "POST",
          });
          const res = await response.json();
          if (!response.ok) throw new Error(res.detail);

          clientState.categorizedEmails = res.categorized_emails;
          renderCategoryList();
        } catch (error) {
          checkCategoryDiv.textContent = "ERROR: " + error.message;
        }
      }
      function renderCategoryList() {
        let html = "<h3>Click a Category to View Subjects:</h3>";
        for (const category in clientState.categorizedEmails) {
          // Note: We pass the category name as a string argument
          html += `<div class="list-item" onclick="renderSubjectList('${category}')">${category} (${clientState.categorizedEmails[category].length} emails)</div>`;
        }
        checkCategoryDiv.innerHTML = html;
      }
      function renderSubjectList(categoryName) {
        const subjects = clientState.categorizedEmails[categoryName];
        let html = `<h3>Subjects in ${categoryName}:</h3>`;
        subjects.forEach((subject) => {
          // Escape quotes in the subject to prevent breaking the HTML string
          const escapedSubject = subject
            .replace(/'/g, "\\'")
            .replace(/"/g, "&quot;");
          html += `<div class="list-item" onclick="renderEmailView('${escapedSubject}')">${subject}</div>`;
        });
        checkCategoryDiv.innerHTML = html;
      }

      function renderEmailView(subject) {
        const body = clientState.subjectsToBody[subject];
        const escapedSubject = subject
          .replace(/'/g, "\\'")
          .replace(/"/g, "&quot;");
        let html = `
          <h3>${subject}</h3>
          <button onclick="summarizeEmail('${escapedSubject}')">Summarize with AI</button>
          <hr>
          <div style="white-space: pre-wrap;">${body || "Body not found."}</div>
      `;
        checkCategoryDiv.innerHTML = html;
      }

      async function summarizeEmail(subject) {
        checkCategoryDiv.innerHTML = "<h3>Summarizing...</h3>";
        try {
          const response = await fetch("/summarizeEmail", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ subject: subject }),
          });
          const res = await response.json();
          if (!response.ok) throw new Error(res.detail);

          let html = `
              <h3>Summary for: ${subject}</h3>
              <div style="white-space: pre-wrap; background-color: #eef; padding: 10px; border-radius: 5px;">${res.summary}</div>
          `;
          checkCategoryDiv.innerHTML = html;
        } catch (error) {
          checkCategoryDiv.innerHTML =
            "<h3>ERROR</h3><p>" + error.message + "</p>";
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
            length = 0
            for email_obj in email_list:
                state.froms.append(email_obj["from"])
                state.subjects.append(email_obj["subject"])
                length +=1
                state.subjects_to_body[email_obj["subject"]] = email_obj["body"]
                state.bodys.append(email_obj["body"])
                if email_obj.get("unread"):
                    state.unreads.append(email_obj["subject"])
            
            return {"success": True, "data": f"Successfully synced and stored {length} emails."}
        else:
            return {"success": False, "data": "Did not receive valid email data from server."}
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error getting mail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/GetCategories")
async def getting_categories():
    """Getting the categories from the server tool."""
    if not state.subjects:
        return {"success": False, "data": "Please sync emails first."}

    try:
        answer = await call_mcp_server("categorize_all_emails")
        if isinstance(answer, TextContent) and answer.text.strip().startswith('{'):
            response_data = json.loads(answer.text)
            print("Server categorization summary received.")
            state.categorized_emails = response_data.get("categories", {})
            print(state.categorized_emails)
            return {"success": True, "data": response_data}
        else:
            error_message = answer.text if isinstance(answer, TextContent) else "Invalid response from server."
            return {"success": False, "data": error_message}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in categorizing through tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/checkCategoryData")
async def check_category_data():
    """Returns the currently stored categorized email data."""
    if not state.categorized_emails:
        raise HTTPException(status_code=400, detail="Please categorize emails first by clicking 'Get Categories'.")
    return {"categorized_emails": state.categorized_emails}

@app.post("/summarizeEmail")
async def summarize_email_endpoint(request: SubjectRequest):
    """Finds an email body by its subject and calls the summarize tool."""
    body = state.subjects_to_body.get(request.subject)
    if not body:
        raise HTTPException(status_code=404, detail="Email subject not found in server state.")

    try:
        summary = await call_mcp_server("summarize", params={"body": body})
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting web client on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)