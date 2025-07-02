from sentence_transformers import SentenceTransformer, util

class ClassifierAgent:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Refined categories with descriptions
        self.categories = {
            "Career / Jobs": "Job alerts, hiring, interview calls, internships, job opportunities, referrals",
            "Social / Networking": "LinkedIn invites, connection requests, social notifications, community updates",
            "Promotions / Offers": "Sales, coupons, discounts, promotional campaigns, cashbacks, special offers",
            "Updates / Newsletters": "News digests, weekly newsletters, platform announcements, blog updates",
            "Events / Reminders": "Event invites, webinars, calendar reminders, upcoming meetings",
            "Security / Notifications": "Login alerts, password resets, suspicious logins, 2FA notifications",
            "Finance / Transactions": "Bills, receipts, invoices, payment confirmations, bank alerts",
            "Education / Learning": "Course updates, certifications, internship results, learning platforms",
            "System / Automated": "System alerts, no-reply bot emails, monitoring logs, uptime/downtime notices",
            "Verification":"verify, verification",
            "Competetive Programming" : "Leetcode , Codechef, GfG, Codeforces",
            "Shopping" : "Order , order!, order",
            "Others": "Emails that don't match any of the above clearly"
        }

        # Pre-compute category embeddings
        self.category_embeddings = {
            name: self.model.encode(desc, convert_to_tensor=True)
            for name, desc in self.categories.items()
        }

    def classify_subject(self, subject: str) -> str:
        if not subject.strip():
            return "Others"
        
        subject_embedding = self.model.encode(subject, convert_to_tensor=True)

        best_match = max(
            self.category_embeddings.items(),
            key=lambda kv: util.pytorch_cos_sim(subject_embedding, kv[1]).item()
        )
        return str(best_match[0])
