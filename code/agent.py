import config
import classifier
from retriever import Retriever
from openai import OpenAI
import json

class SupportAgent:
    def __init__(self):
        self.retriever = Retriever(data_dir=config.DATA_DIR)
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
    def process_ticket(self, issue, subject, company):
        issue_str = str(issue)
        company_str = str(company) if company is not None else ""
        if company_str.lower() == 'nan':
            company_str = ""
            
        # a. Check escalation triggers first
        status, req_type = classifier.classify_request_type(issue_str, self.client)
        if status == "escalated":
            return {
                "status": "escalated",
                "product_area": "security",
                "response": "This ticket has been escalated due to security/legal triggers.",
                "justification": f"Escalated due to trigger: {req_type}",
                "request_type": req_type # Expected output: security_sensitive
            }
            
        # b & c. Route by company field
        domain = company_str.lower() if company_str else None
        
        # d. Call retriever.search()
        query = f"{subject} {issue_str}"
        docs, similarities = self.retriever.search(query, domain=domain, k=5)
        
        # e. If no docs found (similarity < 0.3) -> escalate
        if not docs or max(similarities) < config.SIMILARITY_THRESHOLD:
            return {
                "status": "escalated",
                "product_area": "general",
                "response": "I could not find relevant documentation to answer your query.",
                "justification": f"Low confidence in search results. Max similarity: {max(similarities) if similarities else 0}",
                "request_type": req_type
            }
            
        # f & g. Generate response from docs using LLM & extract product_area
        docs_text = "\n\n".join([f"Source ({doc['source']}):\n{doc['content']}" for doc in docs])
        
        prompt = f"""You are a helpful customer support agent. Answer the user's issue based strictly on the provided documentation.
DO NOT hallucinate. If the docs do not contain the answer, you must state that you cannot answer.

Documentation:
{docs_text}

User Issue:
Subject: {subject}
Body: {issue_str}

Respond in JSON format with exactly these keys:
- "status": "replied" or "escalated" (if docs don't contain answer)
- "response": The answer to the user grounded in docs, including source references. If you cannot answer, say so.
- "justification": Brief reasoning for the response based on docs.
- "product_area": Extracted from docs metadata or inferred from content (e.g. "billing", "account_access", "technical").
"""
        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": "Output strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=config.MAX_TOKENS
            )
            result = json.loads(response.choices[0].message.content)
            
            status = result.get("status", "replied")
            
            # Post-check: if LLM states it cannot answer, escalate
            if status == "escalated" or "cannot answer" in result.get("response", "").lower():
                status = "escalated"
                
            return {
                "status": status,
                "product_area": result.get("product_area", "general"),
                "response": result.get("response", ""),
                "justification": result.get("justification", ""),
                "request_type": req_type
            }
        except Exception as e:
            return {
                "status": "escalated",
                "product_area": "general",
                "response": "API Error occurred while generating response.",
                "justification": str(e),
                "request_type": req_type
            }
