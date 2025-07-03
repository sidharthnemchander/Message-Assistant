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
        state.bodys.append(email_obj["body"])
        state.unreads.append(email_obj["unread"])

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

def view_by_category():
    if not state.categorized_emails:
        print("Please classify emails first using Option 2.")
        return

    print(state.categorized_emails)
    print("\nCategories:")
    for cat , subs in state.categorized_emails.items():
        print(f"\n[{cat}] - {len(subs)} emails")
        for i,s in enumerate(subs):
            print(i + 1,".",s)
    