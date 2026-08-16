import json
from typing import Dict, Any

# Simple baseline rule-based + keyword classifier 
# (Replace/wrap with OpenAI/Ollama/Groq SDK calls when ready)
async def analyze_complaint(title: str, description: str) -> Dict[str, Any]:
    text = f"{title} {description}".lower()

    # Priority determination
    priority = "MEDIUM"
    if any(w in text for w in ["fire", "hazard", "spark", "leak", "overflow", "urgent", "broken lock"]):
        priority = "HIGH"
    elif any(w in text for w in ["noise", "dust", "paint", "cosmetic", "minor"]):
        priority = "LOW"

    # Department and Category routing
    department = "General Maintenance"
    category = "Facility Issue"

    if any(w in text for w in ["ac", "air conditioner", "fan", "power", "light", "socket", "wire"]):
        department = "Electrical & HVAC"
        category = "Electrical"
    elif any(w in text for w in ["water", "pipe", "toilet", "drain", "sink", "tap"]):
        department = "Plumbing"
        category = "Plumbing"
    elif any(w in text for w in ["wifi", "internet", "router", "network", "portal", "login"]):
        department = "IT Support"
        category = "Network"

    return {
        "category": category,
        "priority": priority,
        "department": department
    }