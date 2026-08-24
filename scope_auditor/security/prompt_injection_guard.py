import re
from pydantic import BaseModel, Field

class CleanedCodeContext(BaseModel):
    file_path: str
    raw_content: str
    sanitized_content: str = Field(..., description="Content sanitized of potential prompt injection vector directives.")
    is_suspicious: bool = False
    flagged_reasons: list[str] = Field(default_factory=list)

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s* prompt\s* override",
    r"approve\s+(all\s+)?scope\s+changes",
    r"bypass\s+(security|audit)\s+check",
    r"you\s+are\s+now\s+an?\s+unrestricted",
    r"\[SYSTEM\s+NOTE\]",
]

def sanitize_diff_for_auditing(file_path: str, diff_text: str) -> CleanedCodeContext:
    reasons = []
    suspicious = False
    cleaned_diff = diff_text

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, diff_text, flags=re.IGNORECASE):
            suspicious = True
            reasons.append(f"Matched prompt injection pattern: '{pattern}'")
            cleaned_diff = re.sub(pattern, "[SECURITY_REDACTED_TEXT]", cleaned_diff, flags=re.IGNORECASE)

    return CleanedCodeContext(
        file_path=file_path,
        raw_content=diff_text,
        sanitized_content=cleaned_diff,
        is_suspicious=suspicious,
        flagged_reasons=reasons
    )