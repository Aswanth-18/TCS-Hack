import re
from typing import Optional

def mask_secret(secret: Optional[str]) -> str:
    """Masks secret keys for safe UI/logging display (e.g. sk-proj...1234)."""
    if not secret:
        return "Not Configured"
    if len(secret) <= 8:
        return "****"
    return f"{secret[:4]}...{secret[-4:]}"

def sanitize_prompt(text: str) -> str:
    """Basic sanitizer for prompt logging if needed."""
    if not text:
        return ""
    return text.strip()

