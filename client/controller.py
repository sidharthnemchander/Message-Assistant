from . import state

async def get_emails(session):
    result = await session.call_tool("get_latest_emails")
    state.emails = result.content
    if not state.emails:
        print("No emails found.")
    else:
        print(f"Fetched {len(state.emails)} emails.")

async def categorize_emails(session):
    if not state.emails:
        print("Please fetch emails first (Option 1).")
        return

    state.categorized_emails = {}

    for email in state.emails:
        subject = getattr(email, "subject", "")
        result = await session.call_tool("classify_subject", {"subject": subject})
        
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
            
        state.categorized_emails.setdefault(category, []).append(email)

    print("Emails categorized.")

def view_by_category():
    if not state.categorized_emails:
        print("Please classify emails first using Option 2.")
        return

    print("\nCategories:")
    for category, emails in state.categorized_emails.items():
        print(f"\n[{category}] - {len(emails)} emails")
        for idx, email in enumerate(emails, 1):
            print(f"  {idx}. {getattr(email, "subject", "(No Subject)")}")
