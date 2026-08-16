import json
import logging
from typing import Any, Dict
from groq import AsyncGroq
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert AI triage system for a university campus management platform.
Analyze the complaint title and description provided by the student.

Classify the issue and return a valid JSON object matching this schema exactly:
{
  "category": "Electrical" | "Plumbing" | "Network" | "Facility" | "Cleanliness" | "Security" | "Academic" | "Other",
  "priority": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "department": "Electrical & HVAC" | "Plumbing" | "IT Support" | "Facilities & Maintenance" | "Campus Security" | "Academic Affairs" | "General Administration",
  "reasoning": "A concise 1-sentence explanation of why this category and priority were selected."
}

Rules:
- High/Critical priority: Immediate safety hazards, active water leaks near electronics, power outages, security threats.
- Medium priority: Non-hazardous broken fixtures, localized Wi-Fi problems, AC malfunctions.
- Low priority: Cosmetic issues, minor noise, general queries.
"""


def _rule_based_fallback(title: str, description: str) -> Dict[str, Any]:
    """Fast fallback when LLM API keys are unavailable or rate-limited."""
    text = f"{title} {description}".lower()

    priority = "MEDIUM"
    if any(k in text for k in ["fire", "spark", "smoke", "shock", "flood", "theft", "assault", "lockout"]):
        priority = "CRITICAL" if "fire" in text or "shock" in text else "HIGH"
    elif any(k in text for k in ["paint", "dust", "cosmetic", "suggestion", "slow"]):
        priority = "LOW"

    category = "Facility"
    department = "Facilities & Maintenance"

    if any(k in text for k in ["wifi", "internet", "portal", "login", "server", "lan", "cable"]):
        category = "Network"
        department = "IT Support"
    elif any(k in text for k in ["light", "fan", "ac", "power", "switch", "socket", "voltage"]):
        category = "Electrical"
        department = "Electrical & HVAC"
    elif any(k in text for k in ["pipe", "water", "drain", "sink", "tap", "flush", "sewage"]):
        category = "Plumbing"
        department = "Plumbing"
    elif any(k in text for k in ["guard", "stolen", "id card", "gate", "threat"]):
        category = "Security"
        department = "Campus Security"

    return {
        "category": category,
        "priority": priority,
        "department": department,
        "reasoning": "Classified via heuristic rule engine (fallback mode).",
    }


async def analyze_complaint_llm(title: str, description: str) -> Dict[str, Any]:
    """Runs zero-latency LLM categorization with automated fallback."""
    user_prompt = f"Title: {title}\nDescription: {description}"

    # 1. Try Groq (Llama-3.3-70b / fast inference)
    if settings.GROQ_API_KEY:
        try:
            client = AsyncGroq(api_key=settings.GROQ_API_KEY)
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                model=settings.LLM_MODEL,
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            raw_content = chat_completion.choices[0].message.content
            return json.loads(raw_content)
        except Exception as e:
            logger.warning(f"Groq triage failed: {e}. Attempting fallback.")

    # 2. Try OpenAI (gpt-4o-mini)
    elif settings.OPENAI_API_KEY:
        try:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            raw_content = chat_completion.choices[0].message.content
            return json.loads(raw_content)
        except Exception as e:
            logger.warning(f"OpenAI triage failed: {e}. Attempting fallback.")

    # 3. Fallback Engine
    return _rule_based_fallback(title, description)