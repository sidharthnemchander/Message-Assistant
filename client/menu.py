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
    print("9. Chat with AI about your data")  # New option
    print("10. List available MCP resources")  # New option
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
        await controller.chat_with_ai_about_data(session)
    elif choice == '10':
        # List available resources
        result = await session.call_tool("list_available_resources")
        print("\n=== Available MCP Resources ===")
        print(result.content[0].text)
    elif choice == "11":
        print("Exiting...")
        return False
    else:
        print("Invalid choice.")
    return True