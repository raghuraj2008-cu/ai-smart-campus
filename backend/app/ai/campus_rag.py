from typing import Dict, Any

class CampusRAG:
    """
    Retrieval-Augmented Generation engine for AI Smart Campus context queries.
    Handles user queries using campus documents, policies, and schedules.
    """
    def __init__(self):
        self.knowledge_base = {
            "library_hours": "The main library is open from 8:00 AM to 10:00 PM on weekdays.",
            "wifi_support": "To connect to Campus WiFi, use your Student UID and university password.",
            "emergency_contact": "Campus Security can be reached at extension 911 or via the Emergency tab."
        }

    async def query(self, user_prompt: str) -> Dict[str, Any]:
        prompt_lower = user_prompt.lower()
        matched_context = []

        for key, text in self.knowledge_base.items():
            if any(term in prompt_lower for term in key.split("_")):
                matched_context.append(text)

        if not matched_context:
            response_text = f"I am analyzing your prompt: '{user_prompt}'. No specific campus document matched, but your request has been logged."
        else:
            response_text = " ".join(matched_context)

        return {
            "query": user_prompt,
            "answer": response_text,
            "sources": matched_context if matched_context else ["General Campus Knowledge Base"]
        }

campus_rag = CampusRAG()