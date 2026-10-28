import json
import re
import logging

logger = logging.getLogger("interview_ai.validators")

def sanitize_json_response(raw_text: str) -> str:
    """
    Strips Markdown code fences and whitespace from raw LLM text
    to extract raw JSON strings reliably.
    """
    if not raw_text:
        return "{}"
    
    cleaned = raw_text.strip()
    # Match ```json ... ``` or ``` ... ```
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if json_match:
        cleaned = json_match.group(1).strip()
    
    return cleaned

def parse_llm_json(raw_text: str) -> dict:
    """
    Parses raw LLM text into a Python dictionary.
    Handles extra whitespace, markdown block markers, and JSON decoding errors safely.
    """
    cleaned = sanitize_json_response(raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON decode failed: {e}. Attempting fallback regex extraction...")
        # Fallback: find outer-most curly braces
        brace_match = re.search(r"(\{[\s\S]*\})", raw_text)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except Exception:
                pass
        raise ValueError(f"Could not parse valid JSON from LLM response: {raw_text[:100]}...")

def clamp_score(score: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """Ensures evaluation ratings stay strictly within bounds [0.0, 10.0]."""
    try:
        val = float(score)
        return max(min_val, min(max_val, val))
    except (ValueError, TypeError):
        return 5.0
