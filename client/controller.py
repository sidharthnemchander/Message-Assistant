from . import state
import json
from email.utils import parseaddr
from direct_telegram_test import test_direct

async def get_emails(session):

    result = await session.call_tool("get_latest_emails")

    that_damn_object = result.content[0].text
    data = json.loads(that_damn_object)
    email_data = data["emails"]
    length = 0
    for email_obj in email_data:
        length +=1
        state.froms.append(email_obj["from"])
        state.subjects.append(email_obj["subject"])
        state.subjects_to_body[email_obj["subject"]] = email_obj["body"]
        state.bodys.append(email_obj["body"])
        if email_obj["unread"] == "true" :
            state.unreads.append(email_obj["subject"])

    print("No of emails fetched",length )
    print(state.emails)


async def categorize_emails(session):
    if not state.subjects:
        print("Please fetch emails first (Option 1).")
        return

    state.categorized_emails = {}

    for sub in state.subjects:
        result = await session.call_tool("classify_subject", {"subject": sub})
        
        category = result.content[0].text
        category = str(category)
        
        # Fallback to "Others" if empty
        if not category or category.strip() == "":
            category = "Others"
            
        state.categorized_emails.setdefault(category, []).append(sub)
    print("Emails categorized.")

async def view_by_category(session):
    if not state.categorized_emails:
        print("Please classify emails first using Option 2.")
        return

    print(state.categorized_emails)
    print("\nCategories:")
    cnt = 1
    for cat , subs in state.categorized_emails.items():
        print(f"\n{cnt}.[{cat}] - {len(subs)} emails")
        cnt+=1
        state.num_cat[cnt] = cat
        for i,s in enumerate(subs):
            print(i + 1,".",s)
    
    print("Enter the Category Index to view the emails")
    user_input = int(input())
    req_cat = state.num_cat[user_input+1]
    req_subs = state.categorized_emails[req_cat]

    for i , sub_name in enumerate(req_subs):
        print(i+1,".",sub_name)
        state.sub_ind_to_body[i+1] = state.subjects_to_body[sub_name]
    print("Enter the index of the sub to view")

    sub_view = int(input())
    email = state.sub_ind_to_body[sub_view]
    print(email)

    print("Type 'Y' to use AI for summarization or type something else")

    check = input().strip()

    if(check == 'Y'):
        small_content = await session.call_tool("summarize", {"body": email})
        print(small_content.content[0].text)
    else:
        return

async def send_emails(session):
    """Sending msgs using IMAP protocol"""
    print("Enter the email address you want to send it to : (press 'froms' to check the from addresses)")
    u_inp = input().strip()
    if(u_inp == 'froms'):
        email_addresses = [parseaddr(sender)[1] for sender in state.froms]
        print(email_addresses)
        send_add = input("Enter the address here : ").strip()
    else:
        send_add = u_inp
    
    sub = input("Enter the subject of your email : ").strip()
    body = input("Enter the Body of your email : ")
    await session.call_tool("send_emails", {"subject" : sub, "to" : send_add, "body" : body})

async def send_emails_through_Groq(session):
    print("Enter the email address you want to send it to : (press 'froms' to check the from addresses)")
    # Showing all the current from addresses
    u_inp = input().strip()
    if(u_inp == 'froms'):
        f_list = state.froms
        while f_list == []:
            await get_emails(session)
            f_list = state.froms
        email_addresses = [parseaddr(sender)[1] for sender in state.froms]
        print(email_addresses)
        send_add = input("Enter the address here : ").strip()
    else:
        send_add = u_inp
    prompt = input("Hi Sir, How may i help you : ").strip()

    #Getting Groq's reply
    obj = await session.call_tool("send_mail_by_Groq",{"prompt": prompt})
    groq_reply = obj.content[0].text

    #Calling the send email method
    await session.call_tool("send_emails", {"subject" : "This is a automated reply from Groq", "to" : send_add, "body" : groq_reply})

async def get_t_messages():
    """Fetch and display Telegram messages using direct connection test."""
    data = await test_direct()
    for chat_name , messages in data.items():
        state.name_message[chat_name] = messages
        state.t_names.append(chat_name)
    print(state.name_message)

async def send_t_messages(session):
    """Sending msgs to instagram with usernames"""

    print("Enter the User Name you want to send the message to (Enter 'titles' to see UserNames): ")
    user_input = input().strip()
    
    #Diplaying the titles from the msgs i have got
    if user_input == "titles":
        if state.t_names:
            print("Available usernames:")
            for i, name in enumerate(state.t_names, 1):
                print(f"{i}. {name}")
        else:
            print("No usernames available. Please sync Telegram messages first (Option 6).")
            return None
        user_input = input("Enter the username: ").strip()

    body = input("Enter the message : ").strip()

    result = await session.call_tool("send_telegram_messages", {"to": user_input, "body": body})
    return result

async def send_message_groq(session):
    """Replying to msgs using Groq"""

    print("Enter the User Name you want to send the message to (Enter 'titles' to see UserNames): ")
    user_input = input().strip()
    
    #Diplaying the titles from the msgs i have got
    if user_input == "titles":
        if state.t_names:
            print("Available usernames:")
            for i, name in enumerate(state.t_names, 1):
                print(f"{i}. {name}")
        else:
            print("No usernames available. Please sync Telegram messages first (Option 6).")
            return None
        user_input = input("Enter the username: ").strip()
    
    prompt = input("Hi , How should i draft your message : ").strip()
    #Getting the text to send from groq
    body = await session.call_tool("message_groq", {"prompt": prompt})
    body_text = body.content[0].text
    #Calling the send msg tool
    await session.call_tool("send_telegram_messages", {"to": user_input, "body": body_text})

async def ask_ai_about_emails(session):
    """Ask AI questions about your emails with full context"""
    if not state.subjects:
        print("Please fetch emails first (Option 1).")
        return
    
    print(f"\nYou have {len(state.subjects)} emails loaded.")
    if state.categorized_emails:
        print(f"Categories: {', '.join(state.categorized_emails.keys())}")
    if state.unreads:
        print(f"Unread emails: {len(state.unreads)}")
    
    print("\nAsk me anything about your emails:")
    question = input("Your question: ").strip()
    
    if not question:
        print("No question provided.")
        return
    
    try:
        result = await session.call_tool("ask_about_emails", {"question": question})
        print("\nAI Response:")
        print(result.content[0].text)
    except Exception as e:
        print(f"Error: {e}")

async def show_email_state(session):
    """Show current email state summary"""
    try:
        result = await session.call_tool("query_email_state", {"query_type": "all"})
        data = result.content[0].text
        
        print("\n=== EMAIL STATE SUMMARY ===")
        print(data)
        
        # Also show specific queries
        print("\nWhat would you like to see?")
        print("1. Just subjects")
        print("2. Just categories") 
        print("3. Just unread emails")
        print("4. Just senders")
        print("5. Back to main menu")
        
        choice = input("Enter choice: ").strip()
        
        query_map = {
            "1": "subjects",
            "2": "categories", 
            "3": "unread",
            "4": "senders"
        }
        
        if choice in query_map:
            result = await session.call_tool("query_email_state", {"query_type": query_map[choice]})
            print(f"\n=== {query_map[choice].upper()} ===")
            print(result.content[0].text)
            
    except Exception as e:
        print(f"Error getting email state: {e}")