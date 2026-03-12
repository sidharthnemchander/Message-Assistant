from transformers import pipeline
import re


class ClassifierAgent:

    def __init__(self):

        print("Loading zero-shot model...")

        self.classifier = pipeline(
            "zero-shot-classification",
            model="knowledgator/comprehend_it-base"
        )

        self.categories = [
            "Career / Jobs",
            "Social / Networking",
            "Promotions / Offers",
            "Updates / Newsletters",
            "Events / Reminders",
            "Security / Notifications",
            "Finance / Transactions",
            "Education / Learning",
            "System / Automated",
            "Verification",
            "Competitive Programming",
            "Shopping",
            "Others"
        ]

        # rule-based patterns
        self.rules = {
            "Verification": [
                r"\botp\b",
                r"\bverification code\b",
                r"\bverify your email\b"
            ],
            "Finance / Transactions": [
                r"\binvoice\b",
                r"\breceipt\b",
                r"\bpayment\b",
                r"\bbill\b"
            ],
            "Shopping": [
                r"\border\b",
                r"\bshipment\b",
                r"\bdelivery\b",
                r"\btracking number\b"
            ],
            "Security / Notifications": [
                r"\bpassword reset\b",
                r"\bsuspicious login\b",
                r"\blogin alert\b"
            ],
            "Competitive Programming": [
                r"\bleetcode\b",
                r"\bcodechef\b",
                r"\bcodeforces\b",
                r"\bgfg\b"
            ]
        }

        print("Classifier ready.")


    def rule_based_classify(self, text):

        text = text.lower()

        for category, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return category

        return None


    def zero_shot_classify(self, text):

        result = self.classifier(
            text,
            candidate_labels=self.categories
        )

        return result["labels"][0]


    def classify_subject(self, subject):

        if not subject.strip():
            return "Others"

        print("classifier_agent running")

        rule_result = self.rule_based_classify(subject)

        if rule_result:
            return rule_result

        return self.zero_shot_classify(subject)