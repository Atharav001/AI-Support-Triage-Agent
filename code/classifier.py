import config
from openai import OpenAI
import json

ESCALATION_TRIGGERS = [
    "fraud", "unauthorized", "stolen", "legal", 
    "security breach", "identity theft", "account hacked"
]

def classify_request_type(issue, client=None):
    issue_lower = str(issue).lower()
    
    # Check escalation triggers first
    for trigger in ESCALATION_TRIGGERS:
        if trigger in issue_lower:
            return "escalated", "security_sensitive"
            
    # Simple keyword rules
    if any(kw in issue_lower for kw in ["bug", "error", "exception", "broken", "crash"]):
        req_type = "bug"
    elif any(kw in issue_lower for kw in ["feature", "request", "add", "new", "wish", "idea"]):
        req_type = "feature_request"
    else:
        # LLM Fallback
        if not client:
            client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        prompt = f"""Classify the following issue into EXACTLY ONE of these categories:
"product_issue", "feature_request", "bug", "invalid".

Issue: {issue}

Output ONLY the category name."""
        try:
            response = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            cat = response.choices[0].message.content.strip().lower()
            if cat in ["product_issue", "feature_request", "bug", "invalid"]:
                req_type = cat
            else:
                req_type = "product_issue"
        except Exception:
            req_type = "product_issue"
            
    return "normal", req_type
