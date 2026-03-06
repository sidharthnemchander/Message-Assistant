from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import re


class ClassifierAgent:

    def __init__(self):

        print("Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # categories
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

        # semantic descriptions
        category_texts = [
            "jobs hiring internship interview referral career opportunity",
            "linkedin connection request networking social notification",
            "discount coupon cashback promotional offer sale",
            "newsletter weekly digest blog update announcement",
            "webinar event meeting reminder calendar invite",
            "security login alert suspicious login password reset",
            "invoice bill payment receipt bank transaction payment confirmation",
            "course certification learning platform internship result",
            "system alert monitoring log uptime downtime server alert",
            "verify email phone verification otp confirmation",
            "leetcode codechef codeforces competitive programming contest",
            "order delivery shipment purchase order confirmation tracking",
            "other uncategorized email"
        ]

        print("Building FAISS index...")
        embeddings = self.model.encode(category_texts)
        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings) # type: ignore

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


    def embedding_classify(self, text):

        embedding = self.model.encode([text])
        embedding = np.array(embedding).astype("float32")

        distances, indices = self.index.search(embedding, k=1)# type: ignore

        return self.categories[indices[0][0]]


    def classify_subject(self, subject):

        if not subject.strip():
            return "Others"

        print("classifier_agent running")

        rule_result = self.rule_based_classify(subject)

        if rule_result:
            return rule_result

        return self.embedding_classify(subject)