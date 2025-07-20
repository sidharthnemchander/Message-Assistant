import streamlit as st
import asyncio
import threading
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from email.utils import parseaddr

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Deferred imports to avoid pyrogram's async_to_sync during module loading
def import_controller_and_state():
    try:
        from client.controller import (
            get_emails,
            categorize_emails,
            view_by_category,
            send_emails,
            send_emails_through_Groq,
            get_t_messages,
            send_t_messages,
            send_message_groq,
            chat_with_ai_about_data,
        )
        from client.state import (
            categorized_emails,
            froms,
            subjects,
            unreads,
            subjects_to_body,
            num_cat,
            sub_ind_to_body,
            name_message,
            t_names,
        )
        return locals()
    except Exception as e:
        logger.error(f"Failed to import controller and state: {e}")
        st.error(f"Failed to import controller and state: {e}")
        return {}

# Initialize session state
if "client_session" not in st.session_state:
    st.session_state.client_session = None
    st.session_state.session_initialized = False
    st.session_state.session_error = None
    st.session_state.controller = None
    st.session_state.session_status = "Not initialized"
    st.session_state.session_task = None
    st.session_state.event_loop = None
    st.session_state.loop_thread = None

# Function to run the event loop in a background thread
def run_event_loop(loop):
    try:
        asyncio.set_event_loop(loop)
        loop.run_forever()
    except Exception as e:
        logger.error(f"Event loop error: {e}")
        st.session_state.session_error = f"Event loop error: {e}"
        st.session_state.session_status = "Event loop failed"

# Start the event loop in a background thread if not already started
if st.session_state.loop_thread is None or not st.session_state.loop_thread.is_alive():
    st.session_state.event_loop = asyncio.new_event_loop()
    st.session_state.loop_thread = threading.Thread(
        target=run_event_loop, 
        args=(st.session_state.event_loop,), 
        daemon=True
    )
    st.session_state.loop_thread.start()
    logger.info("Started event loop thread")

# Import controller and state after event loop is set
if st.session_state.controller is None:
    st.session_state.controller = import_controller_and_state()

# Extract imported modules with None checks
categorized_emails = st.session_state.controller.get('categorized_emails', {})
froms = st.session_state.controller.get('froms', [])
subjects = st.session_state.controller.get('subjects', [])
unreads = st.session_state.controller.get('unreads', [])
subjects_to_body = st.session_state.controller.get('subjects_to_body', {})
num_cat = st.session_state.controller.get('num_cat', {})
sub_ind_to_body = st.session_state.controller.get('sub_ind_to_body', {})
name_message = st.session_state.controller.get('name_message', {})
t_names = st.session_state.controller.get('t_names', [])
get_emails = st.session_state.controller.get('get_emails')
categorize_emails = st.session_state.controller.get('categorize_emails')
view_by_category = st.session_state.controller.get('view_by_category')
send_emails = st.session_state.controller.get('send_emails')
send_emails_through_Groq = st.session_state.controller.get('send_emails_through_Groq')
get_t_messages = st.session_state.controller.get('get_t_messages')
send_t_messages = st.session_state.controller.get('send_t_messages')
send_message_groq = st.session_state.controller.get('send_message_groq')
chat_with_ai_about_data = st.session_state.controller.get('chat_with_ai_about_data')

# Streamlit page configuration
st.set_page_config(page_title="Email & Telegram Assistant", layout="wide")

# Function to initialize the client session
async def initialize_session():
    """Initialize MCP client session with proper error handling and lifecycle management."""
    try:
        logger.info("Starting MCP server initialization")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="python",
            args=["-u", "mcp_server.py"]
        )
        
        # Create stdio client connection
        logger.info("Creating stdio client connection")
        read_stream, write_stream = await stdio_client(server_params)
        
        # Create and initialize session
        logger.info("Creating ClientSession")
        session = ClientSession(read_stream, write_stream)
        
        logger.info("Initializing session")
        await session.initialize()
        
        logger.info("MCP server initialized successfully")
        return session, None
        
    except Exception as e:
        logger.error(f"Failed to initialize client session: {e}")
        error_msg = f"Failed to initialize client session: {e}"
        return None, error_msg

# Function to manage session initialization
def initialize_session_sync():
    """Synchronous wrapper to initialize session in background thread."""
    if st.session_state.event_loop is None:
        st.session_state.session_error = "Event loop not available"
        st.session_state.session_status = "Event loop not available"
        return
    
    if st.session_state.session_task is not None and not st.session_state.session_task.done():
        # Already initializing
        return
    
    try:
        st.session_state.session_status = "Initializing MCP session..."
        st.session_state.session_error = None
        
        # Schedule the initialization in the event loop
        future = asyncio.run_coroutine_threadsafe(
            initialize_session(), 
            st.session_state.event_loop
        )
        st.session_state.session_task = future
        
        # Try to get result with short timeout for immediate feedback
        try:
            session, error = future.result(timeout=5.0)
            if error:
                st.session_state.session_error = error
                st.session_state.session_status = f"Initialization failed: {error}"
                st.session_state.session_initialized = False
            else:
                st.session_state.client_session = session
                st.session_state.session_initialized = True
                st.session_state.session_status = "Session initialized successfully"
        except asyncio.TimeoutError:
            st.session_state.session_status = "Initialization in progress..."
            # Check if it completed in background
            if future.done():
                try:
                    session, error = future.result()
                    if error:
                        st.session_state.session_error = error
                        st.session_state.session_status = f"Initialization failed: {error}"
                        st.session_state.session_initialized = False
                    else:
                        st.session_state.client_session = session
                        st.session_state.session_initialized = True
                        st.session_state.session_status = "Session initialized successfully"
                except Exception as e:
                    st.session_state.session_error = f"Initialization error: {e}"
                    st.session_state.session_status = f"Initialization failed: {e}"
                    st.session_state.session_initialized = False
        
    except Exception as e:
        logger.error(f"Error scheduling session initialization: {e}")
        st.session_state.session_error = f"Error scheduling session initialization: {e}"
        st.session_state.session_status = f"Initialization failed: {e}"
        st.session_state.session_initialized = False

# Helper function to run async tasks in the event loop
def run_async_task(coro, timeout=30):
    """Run async task in the background event loop with timeout."""
    if st.session_state.event_loop is None or st.session_state.event_loop.is_closed():
        raise RuntimeError("Event loop not available or closed")
    
    future = asyncio.run_coroutine_threadsafe(coro, st.session_state.event_loop)
    try:
        return future.result(timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Async task timed out after {timeout} seconds")
        raise RuntimeError(f"Operation timed out after {timeout} seconds. Please try again.")

# Check session status on each run
def check_session_status():
    """Check and update session status."""
    if st.session_state.session_task is not None and st.session_state.session_task.done():
        if not st.session_state.session_initialized and st.session_state.session_error is None:
            try:
                session, error = st.session_state.session_task.result()
                if error:
                    st.session_state.session_error = error
                    st.session_state.session_status = f"Initialization failed: {error}"
                    st.session_state.session_initialized = False
                else:
                    st.session_state.client_session = session
                    st.session_state.session_initialized = True
                    st.session_state.session_status = "Session initialized successfully"
            except Exception as e:
                st.session_state.session_error = f"Session check error: {e}"
                st.session_state.session_status = f"Initialization failed: {e}"
                st.session_state.session_initialized = False

# Streamlit UI
st.title("Email & Telegram Assistant")

# Check session status
check_session_status()

# Display session status
col1, col2 = st.columns([3, 1])
with col1:
    st.write(f"**Session Status:** {st.session_state.session_status}")
with col2:
    if not st.session_state.session_initialized:
        if st.button("Initialize Session", type="primary"):
            initialize_session_sync()
            st.rerun()
    else:
        st.success("✓ Ready")

# Display session error if any
if st.session_state.session_error:
    st.error(st.session_state.session_error)
    if st.button("Reset Session"):
        # Reset session state
        st.session_state.client_session = None
        st.session_state.session_initialized = False
        st.session_state.session_error = None
        st.session_state.session_status = "Reset - ready to initialize"
        st.session_state.session_task = None
        st.rerun()

# Only show the main interface if session is initialized
if st.session_state.session_initialized and st.session_state.client_session:
    # Sidebar for navigation
    st.sidebar.header("Menu")
    menu_options = [
        "Get Emails",
        "Get Categories", 
        "View Emails by Category",
        "Send Emails",
        "Send Emails with Bot",
        "Sync Telegram Messages",
        "Send Telegram Messages",
        "Send Telegram Message by Groq",
        "Chat with AI about Data",
        "List Available MCP Resources",
    ]
    selected_option = st.sidebar.selectbox("Select an option", menu_options)

    # Main content area
    if selected_option == "Get Emails":
        st.header("Fetch Latest Emails")
        if st.button("Fetch Emails", disabled=not get_emails):
            try:
                with st.spinner("Fetching emails..."):
                    run_async_task(get_emails(st.session_state.client_session))
                st.success(f"Fetched {len(subjects)} emails!")
                st.write("Recent senders:", froms[-10:])
                st.write("Recent subjects:", subjects[-10:])
                st.write("Unread subjects:", unreads[-10:])
            except Exception as e:
                logger.error(f"Error fetching emails: {e}")
                st.error(f"Error fetching emails: {e}")

    elif selected_option == "Get Categories":
        st.header("Categorize Emails")
        if st.button("Categorize Emails", disabled=not categorize_emails):
            try:
                with st.spinner("Categorizing emails..."):
                    run_async_task(categorize_emails(st.session_state.client_session))
                st.success("Emails categorized successfully!")
                if categorized_emails:
                    st.write("Categories found:")
                    for cat, subs in categorized_emails.items():
                        st.write(f"- {cat}: {len(subs)} emails")
                else:
                    st.warning("No categories available. Please fetch emails first.")
            except Exception as e:
                logger.error(f"Error categorizing emails: {e}")
                st.error(f"Error categorizing emails: {e}")

    elif selected_option == "View Emails by Category":
        st.header("View Emails by Category")
        if not categorized_emails:
            st.warning("No categories available. Please categorize emails first.")
        else:
            category = st.selectbox("Select Category", list(categorized_emails.keys()))
            if st.button("View Emails"):
                num_cat.clear()
                for i, cat in enumerate(categorized_emails.keys(), 1):
                    num_cat[i] = cat
                req_cat = category
                req_subs = categorized_emails[req_cat]
                st.write(f"Emails in {req_cat}:")
                for i, sub_name in enumerate(req_subs, 1):
                    st.write(f"{i}. {sub_name}")
                    sub_ind_to_body[i] = subjects_to_body.get(sub_name, "")
                email_index = st.number_input(
                    "Enter the index of the email to view", min_value=1, max_value=len(req_subs), step=1
                )
                if st.button("View Email"):
                    email_body = sub_ind_to_body.get(email_index, "No body available")
                    st.text_area("Email Content", email_body, height=200)
                    if st.button("Summarize with AI"):
                        try:
                            with st.spinner("Generating summary..."):
                                small_content = run_async_task(
                                    st.session_state.client_session.call_tool("summarize", {"body": email_body})
                                )
                            st.write("Summary:", small_content.content[0].text)
                        except Exception as e:
                            logger.error(f"Error summarizing email: {e}")
                            st.error(f"Error summarizing email: {e}")

    elif selected_option == "Send Emails":
        st.header("Send Emails")
        to_address = st.text_input("To (Enter 'froms' to see available senders)", "")
        if to_address == "froms":
            st.write("Available senders:", [parseaddr(sender)[1] for sender in froms])
            to_address = st.text_input("Enter the email address", "")
        subject = st.text_input("Subject", "")
        body = st.text_area("Body", "", height=200)
        if st.button("Send Email", disabled=not send_emails):
            if to_address and subject and body:
                try:
                    with st.spinner("Sending email..."):
                        run_async_task(
                            send_emails(st.session_state.client_session, to_address=to_address, subject=subject, body=body)
                        )
                    st.success("Email sent successfully!")
                except Exception as e:
                    logger.error(f"Error sending email: {e}")
                    st.error(f"Error sending email: {e}")
            else:
                st.error("Please fill all fields.")

    elif selected_option == "Send Emails with Bot":
        st.header("Send Emails with Groq")
        to_address = st.text_input("To (Enter 'froms' to see available senders)", "")
        if to_address == "froms":
            st.write("Available senders:", [parseaddr(sender)[1] for sender in froms])
            to_address = st.text_input("Enter the email address", "")
        prompt = st.text_area("Prompt for Groq", "", height=100)
        if st.button("Send Email via Groq", disabled=not send_emails_through_Groq):
            if to_address and prompt:
                try:
                    with st.spinner("Generating and sending email..."):
                        run_async_task(send_emails_through_Groq(st.session_state.client_session))
                    st.success("Email sent via Groq!")
                except Exception as e:
                    logger.error(f"Error sending email via Groq: {e}")
                    st.error(f"Error sending email via Groq: {e}")
            else:
                st.error("Please fill all fields.")

    elif selected_option == "Sync Telegram Messages":
        st.header("Sync Telegram Messages")
        if st.button("Sync Messages", disabled=not get_t_messages):
            try:
                with st.spinner("Syncing Telegram messages..."):
                    run_async_task(get_t_messages())
                st.success("Telegram messages synced!")
                st.write("Chat names:", t_names)
                st.write("Messages:", name_message)
            except Exception as e:
                logger.error(f"Error syncing Telegram messages: {e}")
                st.error(f"Error syncing Telegram messages: {e}")

    elif selected_option == "Send Telegram Messages":
        st.header("Send Telegram Messages")
        to_user = st.text_input("To (Enter 'titles' to see usernames)", "")
        if to_user == "titles":
            st.write("Available usernames:", t_names)
            to_user = st.text_input("Enter the username", "")
        body = st.text_area("Message", "", height=200)
        if st.button("Send Message", disabled=not send_t_messages):
            if to_user and body:
                try:
                    with st.spinner("Sending message..."):
                        result = run_async_task(
                            send_t_messages(st.session_state.client_session, to_user=to_user, body=body)
                        )
                    st.success("Message sent successfully!")
                    st.write("Result:", result.content[0].text)
                except Exception as e:
                    logger.error(f"Error sending Telegram message: {e}")
                    st.error(f"Error sending Telegram message: {e}")
            else:
                st.error("Please fill all fields.")

    elif selected_option == "Send Telegram Message by Groq":
        st.header("Send Telegram Message by Groq")
        to_user = st.text_input("To (Enter 'titles' to see usernames)", "")
        if to_user == "titles":
            st.write("Available usernames:", t_names)
            to_user = st.text_input("Enter the username", "")
        prompt = st.text_area("Prompt for Groq", "", height=100)
        if st.button("Send Message via Groq", disabled=not send_message_groq):
            if to_user and prompt:
                try:
                    with st.spinner("Generating and sending message..."):
                        run_async_task(send_message_groq(st.session_state.client_session, to_user=to_user, prompt=prompt))
                    st.success("Message sent via Groq!")
                except Exception as e:
                    logger.error(f"Error sending message via Groq: {e}")
                    st.error(f"Error sending message via Groq: {e}")
            else:
                st.error("Please fill all fields.")

    elif selected_option == "Chat with AI about Data":
        st.header("Chat with AI about Your Data")
        st.write("Ask any questions about your emails or Telegram messages.")
        question = st.text_input("Your question", "")
        if st.button("Ask AI", disabled=not chat_with_ai_about_data):
            if question:
                try:
                    with st.spinner("Getting AI response..."):
                        response = run_async_task(
                            chat_with_ai_about_data(st.session_state.client_session, question=question)
                        )
                    st.write("AI Response:", response.content[0].text)
                except Exception as e:
                    logger.error(f"Error chatting with AI: {e}")
                    st.error(f"Error chatting with AI: {e}")
            else:
                st.error("Please enter a question.")

    elif selected_option == "List Available MCP Resources":
        st.header("List Available MCP Resources")
        if st.button("List Resources"):
            try:
                with st.spinner("Listing resources..."):
                    result = run_async_task(
                        st.session_state.client_session.call_tool("list_available_resources")
                    )
                st.write("Available Resources:", result.content[0].text)
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                st.error(f"Error listing resources: {e}")

else:
    st.info("Please initialize the MCP session to use the application features.")

# Footer
st.write("---")
st.write("Built with Streamlit and MCP Server")