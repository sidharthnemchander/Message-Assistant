import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from email.utils import parseaddr
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from mcp.types import TextContent
from client import state

app = FastAPI(title="Email and Telegram Assistant")

MCP_SERVER_URL = "http://127.0.0.1:8001/mcp/"

# --- Pydantic Models for request validation ---
class SubjectRequest(BaseModel):
    subject: str

class ChatRequest(BaseModel):
    question: str

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class GroqRequest(BaseModel):
    prompt: str

class SendTelegramRequest(BaseModel):
    to: str
    body: str
    
async def call_mcp_server(tool_name: str, params=None):
    """Connects to the persistent MCP HTTP server and calls a tool."""
    try:
        async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                if params != None:

                    if tool_name == "summarize" and "body" in params:
                        result = await session.call_tool(tool_name,{"body": params["body"]})
                    elif tool_name == "send_emails" and isinstance(params, SendEmailRequest):
                        result = await session.call_tool(tool_name,{"subject" : params.subject, "to" : params.to, "body" : params.body})
                    elif tool_name == "send_mail_by_Groq" and isinstance(params,dict):
                        result = await session.call_tool(tool_name,{"prompt": params['prompt'].prompt})
                    elif tool_name == "send_telegram_messages" and isinstance(params,SendTelegramRequest):
                        result = await session.call_tool(tool_name,{"to": params.to, "body": params.body})
                    elif tool_name == "message_groq" and isinstance(params,GroqRequest):
                        result = await session.call_tool(tool_name,{"prompt": params.prompt})
                    elif tool_name == "chat_about_data" and isinstance(params,ChatRequest):
                        print("THE SERVER IS WORKING")
                        print("q",params.question)
                        result = await session.call_tool(tool_name,{"question": params.question})
                else:
                    result = await session.call_tool(tool_name, **(params or {}))
                
                if result.content and isinstance(result.content[0], TextContent):
                    return result.content[0].text
                return "No result or invalid content type"
    except Exception as e:
        print(f"Could not connect to MCP server or call tool: {e}")
        raise HTTPException(status_code=503, detail="MCP server is unavailable.")

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serves the main web interface, now including Telegram functionality."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
      <head>
        <title>Email and Telegram DM Unify</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
          .container { max-width: 1000px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
          button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px 10px 5px 0; }
          button:hover { background: #0056b3; }
          .info-box { margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px; border: 1px solid #e3e3e3; min-height: 50px; }
          .list-item { padding: 8px; cursor: pointer; border-bottom: 1px solid #eee; }
          .list-item:hover { background-color: #e9ecef; }
          #composer { border: 2px solid #007bff; margin-top: 20px; padding: 20px; border-radius: 8px; display: none; }
          .form-group { margin-bottom: 15px; }
          .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
          .form-group input, .form-group textarea { width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box; }
          .form-group textarea { height: 150px; resize: vertical; }
          .form-group .inline-button { margin-left: 10px; padding: 8px 12px; flex-shrink: 0; }
          .address-dropdown { position: relative; display: inline-block; }
          .address-dropdown-content { display: none; position: absolute; background-color: #f9f9f9; min-width: 250px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); z-index: 1; max-height: 200px; overflow-y: auto; border: 1px solid #ddd; }
          #froms-search { margin: 4px; width: calc(100% - 8px); }
          .address-dropdown-content div { color: black; padding: 12px 16px; text-decoration: none; display: block; cursor: pointer; }
          .address-dropdown-content div:hover { background-color: #f1f1f1; }
          .chat-container { border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
          .chat-name { font-weight: bold; color: #0056b3; }
          .message { margin-left: 15px; padding: 5px; border-left: 3px solid #ddd; }
        </style>
      </head>
      <body>
        <div class="container">
            <h1>Email and Telegram Assistant</h1>
            <button onclick="getMails()">1. Get Emails</button>
            <button onclick="getAndRenderCategories()">2. Get & View Categories</button>
            <button onclick="toggleComposer()">Compose Email</button>
            <button onclick="syncTelegram()">Sync Telegram</button>
            <button onclick="toggleTelegramComposer()" style="background-color: #17a2b8;">Send Telegram</button>
            <button onclick="toggleAiChat()" style="background-color: #28a745;">Chat with AI</button>
                        
            <div id="InteractiveView" class="info-box">Get emails, then get & view categories to start.</div>
            <div id="TelegramView" class="info-box" style="display:none;"></div>

            <div id="composer">
                <h3>New Email</h3>
                <div id="composer-status" style="color: green; margin-bottom: 10px; min-height: 1.2em;"></div>
                <div class="form-group">
                    <label for="to-address">To:</label>
                    <div style="display: flex; align-items: center;">
                        <input type="email" id="to-address" placeholder="recipient@example.com">
                        <div class="address-dropdown">
                            <button class="inline-button" onclick="toggleFromsDropdown()">Froms</button>
                            <div id="froms-dropdown" class="address-dropdown-content">
                                <input type="text" id="froms-search" onkeyup="filterFroms()" placeholder="Search addresses...">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="subject">Subject / Groq Prompt:</label>
                     <div style="display: flex; align-items: center;">
                        <input type="text" id="subject" placeholder="Your subject line or AI prompt">
                        <button class="inline-button" onclick="getGroqHelp()">Help from Groq</button>
                    </div>
                </div>
                <div class="form-group">
                    <label for="body">Body:</label>
                    <textarea id="body"></textarea>
                </div>
                <button onclick="sendEmail()">Send Email</button>
            </div>
        </div>
        <!-- NEW: Telegram Composer -->
            <div id="telegram-composer">
                <h3>New Telegram Message</h3>
                <div id="telegram-composer-status" style="color: #17a2b8; margin-bottom: 10px; min-height: 1.2em;"></div>
                <div class="form-group">
                    <label for="telegram-to-address">To:</label>
                    <div style="display: flex; align-items: center;">
                        <input type="text" id="telegram-to-address" placeholder="Username or Chat Name">
                        <div class="address-dropdown">
                            <button class="inline-button" onclick="toggleUsernamesDropdown()">Usernames</button>
                            <div id="usernames-dropdown" class="address-dropdown-content">
                                <input type="text" id="usernames-search" onkeyup="filterUsernames()" placeholder="Search usernames...">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label for="telegram-body">Message / Groq Prompt:</label>
                    <div style="display: flex; align-items: center;">
                        <textarea id="telegram-body" style="height: 100px;"></textarea>
                        <button class="inline-button" onclick="getTelegramGroqHelp()">Help from Groq</button>
                    </div>
                </div>
                <button onclick="sendTelegramMessage()" style="background-color: #17a2b8;">Send Message</button>
            </div>
            <div id="ai-chat-container">
                <h3>Chat with AI about your Data</h3>
                <p>Ask any questions about your emails, categories, unread messages, telegram chats, etc.</p>
                <div class="form-group">
                    <input type="text" id="ai-chat-question" placeholder="e.g., 'Do I have any unread emails from marketing?'">
                </div>
                <button onclick="askAiAboutData()" style="background-color: #28a745;">Ask AI</button>
                <div id="ai-chat-response" class="info-box" style="white-space: pre-wrap; margin-top: 15px; min-height: 50px;">Your answer will appear here.</div>
            </div>        
        </div>
        <script>
          // --- DOM Elements ---
          const interactiveDiv = document.getElementById("InteractiveView");
          const telegramDiv = document.getElementById("TelegramView");
          const composerDiv = document.getElementById("composer");
          const telegramComposerDiv = document.getElementById("telegram-composer");
          const aiChatContainer = document.getElementById("ai-chat-container");
          const aiChatResponseDiv = document.getElementById("ai-chat-response");
          
          let clientState = { subjectsToBody: {}, categorizedEmails: {}, fromAddresses: [],telegramUsernames: [] };

          // --- Interactive View Functions ---
          async function getMails() {
            interactiveDiv.textContent = "Loading emails...";
            try {
              const response = await fetch("/getMail", { method: "POST" });
              const res = await response.json();
              if (!response.ok) throw new Error(res.detail);
              clientState.subjectsToBody = res.subjects_to_body || {};
              interactiveDiv.textContent = res.message;
            } catch (error) {
              interactiveDiv.textContent = "Error: " + error.message;
            }
          }

          async function getAndRenderCategories() {
            interactiveDiv.textContent = "Categorizing emails...";
            try {
              const response = await fetch("/GetCategories", { method: "POST" });
              const res = await response.json();
              if (!response.ok) throw new Error(res.detail);
              clientState.categorizedEmails = res.categorized_emails || {};
              renderCategoryList();
            } catch (error) {
              interactiveDiv.textContent = "ERROR: " + error.message;
            }
          }
          
          function renderCategoryList() {
              interactiveDiv.innerHTML = '';
              const title = document.createElement('h3');
              title.textContent = 'Click a Category to View Subjects:';
              interactiveDiv.appendChild(title);

              if (Object.keys(clientState.categorizedEmails).length === 0) {
                  const p = document.createElement('p');
                  p.textContent = 'No categories found.';
                  interactiveDiv.appendChild(p);
                  return;
              }

              for (const category in clientState.categorizedEmails) {
                  const subjects = clientState.categorizedEmails[category];
                  if (!Array.isArray(subjects)) continue;

                  const listItem = document.createElement('div');
                  listItem.className = 'list-item';
                  listItem.textContent = category + ' (' + subjects.length + ' emails)';
                  listItem.addEventListener('click', () => renderSubjectList(category));
                  interactiveDiv.appendChild(listItem);
              }
          }

          function renderSubjectList(categoryName) {
              const subjects = clientState.categorizedEmails[categoryName];
              interactiveDiv.innerHTML = '';
              const title = document.createElement('h3');
              title.textContent = 'Subjects in ' + categoryName + ':';
              interactiveDiv.appendChild(title);

              if (!Array.isArray(subjects)) {
                  interactiveDiv.innerHTML += '<p>Error: Subject list is not valid.</p>';
                  return;
              }

              subjects.forEach((subject, index) => {
                  const listItem = document.createElement('div');
                  listItem.className = 'list-item';
                  listItem.textContent = (index + 1) + '. ' + subject;
                  listItem.addEventListener('click', () => renderEmailView(subject));
                  interactiveDiv.appendChild(listItem);
              });
          }

          function renderEmailView(subject) {
              const body = clientState.subjectsToBody[subject];
              interactiveDiv.innerHTML = '';

              const subjectHeader = document.createElement('h3');
              subjectHeader.textContent = subject;

              const summarizeBtn = document.createElement('button');
              summarizeBtn.textContent = 'Summarize with AI';
              summarizeBtn.addEventListener('click', () => summarizeEmail(subject));

              const hr = document.createElement('hr');

              const bodyDiv = document.createElement('div');
              bodyDiv.style.whiteSpace = 'pre-wrap';
              bodyDiv.textContent = body || 'Body not found.';

              interactiveDiv.appendChild(subjectHeader);
              interactiveDiv.appendChild(summarizeBtn);
              interactiveDiv.appendChild(hr);
              interactiveDiv.appendChild(bodyDiv);
          }

          async function summarizeEmail(subject) {
              interactiveDiv.innerHTML = "<h3>Summarizing...</h3>";
              try {
                  const response = await fetch("/summarizeEmail", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ subject: subject })
                  });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);

                  interactiveDiv.innerHTML = '';

                  const summaryHeader = document.createElement('h3');
                  summaryHeader.textContent = 'Summary for: ' + subject;

                  const summaryDiv = document.createElement('div');
                  summaryDiv.style.whiteSpace = 'pre-wrap';
                  summaryDiv.style.backgroundColor = '#eef';
                  summaryDiv.style.padding = '10px';
                  summaryDiv.style.borderRadius = '5px';
                  summaryDiv.textContent = res.summary;

                  const hr = document.createElement('hr');

                  const backBtn = document.createElement('button');
                  backBtn.textContent = 'Back to Categories';
                  backBtn.addEventListener('click', renderCategoryList);

                  interactiveDiv.appendChild(summaryHeader);
                  interactiveDiv.appendChild(summaryDiv);
                  interactiveDiv.appendChild(hr);
                  interactiveDiv.appendChild(backBtn);

              } catch (error) {
                  interactiveDiv.innerHTML = "<h3>ERROR</h3><p>" + error.message + "</p>";
              }
          }

          // --- Email Composer Functions ---
          let fromsVisible = false;
          function toggleComposer() {
              const shouldBeVisible = composerDiv.style.display === 'none';
              composerDiv.style.display = shouldBeVisible ? 'block' : 'none';
              if (shouldBeVisible) {
                  populateFroms();
              }
          }

          async function populateFroms() {
              try {
                  const response = await fetch("/getFromAddresses", { method: "POST" });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);
                  
                  clientState.fromAddresses = res.from_addresses || [];
                  const dropdownContent = document.getElementById("froms-dropdown");
                  dropdownContent.querySelectorAll('div').forEach(el => el.remove());

                  clientState.fromAddresses.forEach(addr => {
                      const item = document.createElement('div');
                      item.textContent = addr;
                      item.onclick = () => {
                          document.getElementById('to-address').value = addr;
                          toggleFromsDropdown(false);
                      };
                      dropdownContent.appendChild(item);
                  });
              } catch(error) {
                  console.error("Failed to populate froms:", error);
              }
          }
          
          function toggleFromsDropdown(forceState) {
              const dropdown = document.getElementById("froms-dropdown");
              fromsVisible = forceState !== undefined ? forceState : !fromsVisible;
              dropdown.style.display = fromsVisible ? 'block' : 'none';
          }

          function filterFroms() {
              const input = document.getElementById("froms-search");
              const filter = input.value.toUpperCase();
              const dropdownContent = document.getElementById("froms-dropdown");
              const items = dropdownContent.querySelectorAll("div");
              items.forEach(item => {
                  let txtValue = item.textContent || item.innerText;
                  item.style.display = txtValue.toUpperCase().indexOf(filter) > -1 ? "" : "none";
              });
          }

          async function getGroqHelp() {
              const promptInput = document.getElementById('subject');
              const bodyTextarea = document.getElementById('body');
              const statusDiv = document.getElementById('composer-status');
              
              if (!promptInput.value) {
                  statusDiv.textContent = "Please enter a prompt for Groq in the subject field.";
                  return;
              }
              statusDiv.textContent = "Asking Groq for help...";
              bodyTextarea.value = "Generating...";

              try {
                  const response = await fetch("/generateEmailBody", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ prompt: promptInput.value })
                  });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);
                  
                  bodyTextarea.value = res.body;
                  promptInput.value = "This is an automated reply from Groq";
                  statusDiv.textContent = "Groq's reply generated!";
              } catch (error) {
                  statusDiv.textContent = "Error: " + error.message;
                  bodyTextarea.value = "Failed to get reply from Groq.";
              }
          }

          async function sendEmail() {
              const to = document.getElementById('to-address').value;
              const subject = document.getElementById('subject').value;
              const body = document.getElementById('body').value;
              const statusDiv = document.getElementById('composer-status');

              if (!to || !subject) {
                  statusDiv.textContent = "Error: 'To' and 'Subject' fields are required.";
                  return;
              }
              statusDiv.textContent = "Sending...";

              try {
                  const response = await fetch("/sendEmail", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ to: to, subject: subject, body: body })
                  });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);
                  statusDiv.textContent = "Email sent successfully! Response: " + res.message;
              } catch(error) {
                  statusDiv.textContent = "Error sending email: " + error.message;
              }
          }

          async function syncTelegram() {
              telegramDiv.style.display = 'block';
              telegramDiv.innerHTML = '<h4>Syncing Telegram messages...</h4>';
              try {
                  const response = await fetch("/syncTelegram", { method: "POST" });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);
                  
                  renderTelegramMessages(res.messages);
              } catch (error) {
                  telegramDiv.innerHTML = '<h4>Error syncing Telegram:</h4><p>' + error.message + '</p>';
              }
          }

          function renderTelegramMessages(data) {
              telegramDiv.innerHTML = '<h3>Telegram Chats</h3>';
              if (!data || Object.keys(data).length === 0) {
                  telegramDiv.innerHTML += '<p>No messages found.</p>';
                  return;
              }

              for (const chatName in data) {
                  if (chatName === "None" || !Array.isArray(data[chatName])) continue;

                  const chatContainer = document.createElement('div');
                  chatContainer.className = 'chat-container';

                  const nameHeader = document.createElement('div');
                  nameHeader.className = 'chat-name';
                  nameHeader.textContent = 'CHAT NAME: ' + chatName;
                  chatContainer.appendChild(nameHeader);

                  data[chatName].forEach((message, index) => {
                      const messageDiv = document.createElement('div');
                      messageDiv.className = 'message';
                      messageDiv.textContent = (index + 1) + '. ' + message;
                      chatContainer.appendChild(messageDiv);
                  });
                  telegramDiv.appendChild(chatContainer);
              }
          }
            let usernamesVisible = false;
          function toggleTelegramComposer() {
              const shouldBeVisible = telegramComposerDiv.style.display === 'none';
              telegramComposerDiv.style.display = shouldBeVisible ? 'block' : 'none';
              if (shouldBeVisible) {
                  populateTelegramUsernames();
              }
          }

          function populateTelegramUsernames() {
              const dropdownContent = document.getElementById("usernames-dropdown");
              dropdownContent.innerHTML = '<input type="text" id="usernames-search" onkeyup="filterUsernames()" placeholder="Search usernames...">';
              if (clientState.telegramUsernames.length === 0) {
                  const item = document.createElement('div');
                  item.textContent = "Sync Telegram first";
                  dropdownContent.appendChild(item);
                  return;
              }
              clientState.telegramUsernames.forEach(name => {
                  const item = document.createElement('div');
                  item.textContent = name;
                  item.onclick = () => {
                      document.getElementById('telegram-to-address').value = name;
                      toggleUsernamesDropdown(false);
                  };
                  dropdownContent.appendChild(item);
              });
          }

          function toggleUsernamesDropdown(forceState) {
              const dropdown = document.getElementById("usernames-dropdown");
              usernamesVisible = forceState !== undefined ? forceState : !usernamesVisible;
              dropdown.style.display = usernamesVisible ? 'block' : 'none';
          }

          function filterUsernames() {
              const filter = document.getElementById("usernames-search").value.toUpperCase();
              const items = document.getElementById("usernames-dropdown").querySelectorAll("div");
              items.forEach(item => {
                  item.style.display = item.textContent.toUpperCase().indexOf(filter) > -1 ? "" : "none";
              });
          }

          async function getTelegramGroqHelp() {
              const bodyTextarea = document.getElementById('telegram-body');
              const statusDiv = document.getElementById('telegram-composer-status');
              const prompt = bodyTextarea.value;

              if (!prompt) {
                  statusDiv.textContent = "Please enter a prompt in the message box to get help from Groq.";
                  return;
              }
              statusDiv.textContent = "Asking Groq for help...";
              bodyTextarea.value = "Generating...";

              try {
                  const response = await fetch("/generateTelegramMessage", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ prompt: prompt })
                  });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);
                  
                  bodyTextarea.value = res.body;
                  statusDiv.textContent = "Groq's reply generated!";
              } catch (error) {
                  statusDiv.textContent = "Error: " + error.message;
                  bodyTextarea.value = "Failed to get reply from Groq.";
              }
          }

          async function sendTelegramMessage() {
              const to = document.getElementById('telegram-to-address').value;
              const body = document.getElementById('telegram-body').value;
              const statusDiv = document.getElementById('telegram-composer-status');

              if (!to || !body) {
                  statusDiv.textContent = "Error: 'To' and 'Message' fields are required.";
                  return;
              }
              statusDiv.textContent = "Sending...";

              try {
                  const response = await fetch("/sendTelegramMessage", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ to: to, body: body })
                  });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);
                  statusDiv.textContent = "Message sent successfully! Response: " + res.message;
              } catch(error) {
                  statusDiv.textContent = "Error sending message: " + error.message;
              }
          }
          function toggleAiChat() {
              const shouldBeVisible = aiChatContainer.style.display === 'none';
              aiChatContainer.style.display = shouldBeVisible ? 'block' : 'none';
          }

          async function askAiAboutData() {
              const questionInput = document.getElementById('ai-chat-question');
              const question = questionInput.value;

              if (!question.trim()) {
                  aiChatResponseDiv.textContent = "Please enter a question.";
                  return;
              }
              aiChatResponseDiv.textContent = "Asking AI...";

              try {
                  const response = await fetch("/chatAboutData", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ question: question })
                  });
                  const res = await response.json();
                  if (!response.ok) throw new Error(res.detail);
                  
                  aiChatResponseDiv.textContent = res.answer;
                  questionInput.value = ''; // Clear input after asking
              } catch (error) {
                  aiChatResponseDiv.textContent = "Error: " + error.message;
              }
          }
        </script>
      </body>
    </html>
    """)

# --- Endpoints for Interactive View & Composer ---
@app.post("/getMail")
async def getting_mail():
    """Fetches emails and returns the subject-to-body map to the client."""
    try:
        raw_response = await call_mcp_server("get_latest_emails")
        data = json.loads(raw_response)
        email_list = data.get('emails', [])

        state.froms = [email.get('from', '') for email in email_list]
        state.subjects_to_body = {email["subject"]: email["body"] for email in email_list}
        state.subjects = list(state.subjects_to_body.keys())
        
        return {
            "message": f"Successfully synced {len(email_list)} emails. You can now Get & View Categories.",
            "subjects_to_body": state.subjects_to_body
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/GetCategories")
async def getting_categories():
    """Calls the categorization tool and returns the result to the client."""
    if not state.subjects:
        raise HTTPException(status_code=400, detail="Please sync emails first.")
    try:
        raw_response = await call_mcp_server("categorize_all_emails")
        response_data = json.loads(raw_response)
        state.categorized_emails = response_data.get("categories", {})
        return { "categorized_emails": state.categorized_emails }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarizeEmail")
async def summarize_email_endpoint(request: SubjectRequest):
    """Finds an email body and calls the summarize tool."""
    body = state.subjects_to_body.get(request.subject)
    if not body:
        raise HTTPException(status_code=404, detail="Email subject not found.")
    try:
        summary = await call_mcp_server("summarize", params={"body": body})
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/getFromAddresses")
async def get_from_addresses():
    """Parses and returns a unique list of sender email addresses."""
    if not state.froms:
        await getting_mail()

    unique_addresses = set()
    for sender in state.froms:
        name, addr = parseaddr(sender)
        if addr:
            unique_addresses.add(addr)
            
    return {"from_addresses": sorted(list(unique_addresses))}

@app.post("/sendEmail")
async def send_email_endpoint(request: SendEmailRequest):
    """Endpoint to send a standard email."""
    try:
        result = await call_mcp_server("send_emails", params=request)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generateEmailBody")
async def generate_email_body_endpoint(request: GroqRequest):
    """Endpoint to get help from Groq."""
    try:
        print("TYPE : ", type(request))
        body = await call_mcp_server("send_mail_by_Groq", params={"prompt": request})
        return {"body": body}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/syncTelegram")
async def sync_telegram_endpoint():
    """Endpoint to fetch and return Telegram messages."""
    try:
        print("Calling the api")
        raw_response = await call_mcp_server("get_telegram_messages")
        print("Got an response")
        messages = json.loads(raw_response)
        print(messages)
        if "error" in messages:
            raise HTTPException(status_code=500, detail=messages["error"])
            
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sendTelegramMessage")
async def send_telegram_message_endpoint(request: SendTelegramRequest):
    """Endpoint to send a Telegram message."""
    try:
        result = await call_mcp_server("send_telegram_messages", params=request)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generateTelegramMessage")
async def generate_telegram_message_endpoint(request: GroqRequest):
    """Endpoint to get help from Groq for Telegram messages."""
    try:
        body = await call_mcp_server("message_groq", params=request)
        return {"body": body}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/chatAboutData")
async def chat_about_data_endpoint(request: ChatRequest):
    """Endpoint to chat with the AI about available data."""
    try:
        answer = await call_mcp_server("chat_about_data", params=request)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting web client on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
