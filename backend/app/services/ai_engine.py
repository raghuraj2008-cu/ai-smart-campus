from app.models.domain import PriorityLevel

class CampusAIEngine:
    def __init__(self):
        self.categories = {
            "Infrastructure": ["ac", "fan", "light", "door", "bench", "water", "pipe", "leak", "building"],
            "IT Support": ["wifi", "internet", "projector", "computer", "lab", "portal", "login", "server"],
            "Security": ["stolen", "unauthorized", "fight", "key", "lock", "cctv", "threat", "emergency"]
        }
        self.departments = {
            "Infrastructure": "Maintenance & Estates",
            "IT Support": "Campus IT Services",
            "Security": "Campus Security Division"
        }

    def analyze_complaint(self, description: str):
        desc_lower = description.lower()
        
        matched_category = "General Maintenance"
        for category, keywords in self.categories.items():
            if any(word in desc_lower for word in keywords):
                matched_category = category
                break

        priority = PriorityLevel.MEDIUM
        if any(w in desc_lower for w in ["urgent", "fire", "danger", "hazard", "not working", "smoke", "leak"]):
            priority = PriorityLevel.HIGH
        if any(w in desc_lower for w in ["short circuit", "collapse", "burst", "weapon", "critical"]):
            priority = PriorityLevel.CRITICAL

        department = self.departments.get(matched_category, "General Administration")

        return {
            "category": matched_category,
            "priority": priority,
            "department": department
        }

ai_engine = CampusAIEngine()
