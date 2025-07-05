from . import controller

def show_menu():
    print("\nOptions:")
    print("1. Get Emails")
    print("2. Get Categories")
    print("3. View Emails by Category")
    print("4. Send Emails")
    print("5. Send Emails with Bot")
    print("6. Sync Telegram messages")
    print("7. Exit")

async def handle_choice(choice: str, session):
    if choice == "1":
        await controller.get_emails(session)
    elif choice == "2":
        await controller.categorize_emails(session)
    elif choice == "3":
        await controller.view_by_category(session)
    elif choice == "7":
        print("Exiting...")
        return False
    elif choice == "4":
        await controller.send_emails(session)
    elif choice == "5":
        await controller.send_emails_through_Groq(session)
    elif choice ==  '6':
        await controller.get_t_messages(session)
    else:
        print("Invalid choice.")
    return True
