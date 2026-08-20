import httpx
import json
from typing import Optional, Dict, Any
from .config import settings


class OllamaClient:
    """Client for interacting with local Ollama/vLLM API."""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048
    ) -> str:
        """Generate text using the local Ollama API."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                return response.json().get("response", "")
            except httpx.HTTPError as e:
                raise RuntimeError(f"Ollama API error: {e}")
    
    async def extract_email_data(self, email_body: str) -> Dict[str, Any]:
        """
        Extract structured data from an email using the local LLM.
        Returns: {client_name, project, change_log: [], drafted_reply}
        """
        system_prompt = """You are an assistant for an interior architect specializing in high-end restaurant design.
Your task is to analyze emails about design revisions and extract:
1. Client name (if mentioned)
2. Project name (if mentioned)  
3. A bullet-point change log of all requested revisions
4. A professional, concise draft reply acknowledging the changes

Respond ONLY with valid JSON in this exact format:
{
    "client_name": "...",
    "project": "...",
    "change_log": ["change 1", "change 2"],
    "drafted_reply": "Professional reply text..."
}

If any field cannot be determined, use null or empty string/array."""

        prompt = f"""Analyze this design revision email and extract the required information:

---EMAIL BODY---
{email_body}
---END EMAIL---

Extract the data as JSON:"""

        response_text = await self.generate(prompt, system_prompt=system_prompt)
        
        # Parse JSON response
        try:
            # Try to find JSON block in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback: return structured empty data
        return {
            "client_name": None,
            "project": None,
            "change_log": [],
            "drafted_reply": f"Thank you for your email. We have received your revision requests and will review them shortly."
        }


ollama_client = OllamaClient()
