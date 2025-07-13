from . import controller

def show_menu():
    print("\nOptions:")
    print("1. Get Emails")
    print("2. Get Categories")
    print("3. View Emails by Category")
    print("4. Send Emails")
    print("5. Send Emails with Bot")
    print("6. Sync Telegram messages")
    print("7. Send Telegram messages")
    print("8. Send Telegram message by Groq")
    print("9. Ask AI (classic Chatbot)")
    print("10. Full Mail Summary")
    print("11. Exit")

async def handle_choice(choice: str, session):
    if choice == "1":
        await controller.get_emails(session)
    elif choice == "2":
        await controller.categorize_emails(session)
    elif choice == "3":
        await controller.view_by_category(session)
    elif choice == "4":
        await controller.send_emails(session)
    elif choice == "5":
        await controller.send_emails_through_Groq(session)
    elif choice == "6":
        await controller.get_t_messages()
    elif choice == '7':
        await controller.send_t_messages(session)
    elif choice == '8':
        await controller.send_message_groq(session)
    elif choice == '9':
        await controller.ask_ai_about_emails(session)
    elif choice == '10':
        await controller.show_email_state(session)
    elif choice == "11":
        print("Exiting...")
        return False
    else:
        print("Invalid choice.")
    return True
