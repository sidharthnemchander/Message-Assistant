from . import controller

def show_menu():
    print("\nOptions:")
    print("1. Get Emails")
    print("2. Get Categories")
    print("3. View Emails by Category")
    print("4. Send Emails")
    print("5. Exit")

async def handle_choice(choice: str, session):
    if choice == "1":
        await controller.get_emails(session)
    elif choice == "2":
        await controller.categorize_emails(session)
    elif choice == "3":
        await controller.view_by_category(session)
    elif choice == "5":
        print("Exiting...")
        return False
    elif choice == "4":
        await controller.send_emails(session)
    else:
        print("Invalid choice.")
    return True
