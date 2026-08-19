import re
from typing import Dict, Any

CATEGORY_KEYWORDS = {
    "ACADEMIC": ["lab", "projector", "exam", "grade", "professor", "class", "lecture", "wifi", "internet"],
    "FACILITY": ["ac", "air conditioner", "water", "leak", "light", "fan", "electricity", "washroom", "plumbing"],
    "HOSTEL": ["room", "bed", "mess", "food", "hostel", "warden", "laundry"],
    "SECURITY": ["theft", "lost", "fight", "guard", "gate", "threat", "emergency", "fire", "smoke"]
}

SEVERITY_KEYWORDS = {
    "HIGH": ["fire", "smoke", "spark", "electric shock", "danger", "medical", "urgent", "theft", "unconscious", "bleeding"],
    "MEDIUM": ["leak", "broken", "flickering", "unstable", "intermittent", "not working"],
    "LOW": ["slow", "dirty", "paint", "noise", "feedback"]
}

def analyze_complaint_ai(title: str, description: str) -> Dict[str, Any]:
    text = f"{title} {description}".lower()
    
    # 1. Category Classification
    assigned_category = "FACILITY"
    max_cat_matches = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text))
        if matches > max_cat_matches:
            max_cat_matches = matches
            assigned_category = cat
            
    # 2. Severity & Priority Scoring
    priority = "NORMAL"
    for kw in SEVERITY_KEYWORDS["HIGH"]:
        if re.search(r'\b' + re.escape(kw) + r'\b', text):
            priority = "URGENT"
            break
            
    if priority != "URGENT":
        for kw in SEVERITY_KEYWORDS["MEDIUM"]:
            if re.search(r'\b' + re.escape(kw) + r'\b', text):
                priority = "MEDIUM"
                break

    return {
        "suggested_category": assigned_category,
        "priority": priority,
        "is_emergency": priority == "URGENT"
    }
