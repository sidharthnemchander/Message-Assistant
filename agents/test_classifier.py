from Classifier import ClassifierAgent


def run_tests():

    classifier = ClassifierAgent()

    test_cases = [
        ("Your Amazon order has been shipped", "Shopping"),
        ("Your OTP for login is 123456", "Verification"),
        ("New job opportunity at Microsoft", "Career / Jobs"),
        ("Weekly LeetCode contest results", "Competitive Programming"),
        ("You received a new LinkedIn connection request", "Social / Networking"),
        ("Your payment receipt for electricity bill", "Finance / Transactions"),
        ("Reminder: Webinar starting in 30 minutes", "Events / Reminders"),
        ("Password reset request", "Security / Notifications"),
        ("New course available on Coursera", "Education / Learning"),
        ("50% discount on all electronics today", "Promotions / Offers"),
    ]

    correct = 0

    for subject, expected in test_cases:

        prediction = classifier.classify_subject(subject)

        result = "PASS" if prediction == expected else "FAIL"

        print(f"\nSubject: {subject}")
        print(f"Expected: {expected}")
        print(f"Predicted: {prediction}")
        print(f"Result: {result}")

        if result == "PASS":
            correct += 1

    print("\n---------------------")
    print(f"Accuracy: {correct}/{len(test_cases)}")


if __name__ == "__main__":
    run_tests()