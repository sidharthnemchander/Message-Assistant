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
    await session.call_tool("send_emails", {"subject" : "This is a automated reply from groq", "to" : send_add, "body" : groq_reply})

async def get_t_messages(session):
    """Fetch and display Telegram messages using direct connection test."""
    print("Controller: Using direct Telegram connection via direct_telegram_test...")
    try:
        data = await test_direct()
        for chat_id , messages in data.items():
            state.id_message[chat_id] = messages
    except Exception as e:
        print(f"Controller: direct_telegram_test failed: {e}")
        import traceback; traceback.print_exc()