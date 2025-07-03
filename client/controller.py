from . import state
import json

async def get_emails(session):
    print("The controller is running")
    
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

    print(state.subjects)
    print("No of emails fetched",length )


async def categorize_emails(session):
    print("The controller.py is running")
    if not state.subjects:
        print("Please fetch emails first (Option 1).")
        return

    state.categorized_emails = {}

    for sub in state.subjects:
        result = await session.call_tool("classify_subject", {"subject": sub})
        
        # Extract category from nested structure
        category = result.content
        
        # Handle nested lists/structures
        while isinstance(category, list) and category:
            category = category[0]
        
        # Only try to access attributes if it's not a list
        if not isinstance(category, list):
            # Extract text from TextContent object
            if hasattr(category, 'text'):
                category = category.text
            elif hasattr(category, 'content'):
                category = category.content
            else:
                category = str(category)
        else:
            # If it's still a list, convert to string
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
        print(f"\n{cnt}[{cat}] - {len(subs)} emails")
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
        print("THIS IS WORKING")
        small_content = await session.call_tool("summarize", {"body": email})
        print(small_content)
    else:
        return