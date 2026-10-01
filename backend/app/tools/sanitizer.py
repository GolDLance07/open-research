import re
import unicodedata
from typing import List, Tuple

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior)\s+rules?",
    r"system\s*:\s*you\s+are",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"dan\s+mode|jailbreak",
    r"output\s+the\s+(entire\s+)?system\s+prompt",
    r"admin\s+override",
    r"<untrusted_source",
    r"</untrusted_source>",
]

COMPILED_INJECTION_REGEX = [
    re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS
]


def check_injection_patterns(text: str) -> List[str]:
    """Check if text contains suspicious prompt injection patterns."""
    matched = []
    for pattern in COMPILED_INJECTION_REGEX:
        if pattern.search(text):
            matched.append(pattern.pattern)
    return matched


def sanitize_text(text: str, max_chars: int = 50000) -> Tuple[str, bool, List[str]]:
    """Clean and sanitize untrusted retrieved text.
    Returns (cleaned_text, injection_flagged, flagged_patterns).
    """
    if not text:
        return "", False, []

    # 1. Normalize Unicode
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Remove control characters (except newline, tab)
    cleaned = "".join(
        ch for ch in normalized if ch == "\n" or ch == "\t" or not unicodedata.category(ch).startswith("C")
    )

    # 3. Escape/strip untrusted source delimiter tags to preserve delimiter integrity
    cleaned = cleaned.replace("<untrusted_source>", "&lt;untrusted_source&gt;")
    cleaned = cleaned.replace("</untrusted_source>", "&lt;/untrusted_source&gt;")

    # 4. Check injection patterns
    flagged = check_injection_patterns(cleaned)
    has_injection = len(flagged) > 0

    # 5. Collapse excessive whitespace
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # 6. Truncate to max chars
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n...[truncated]"

    return cleaned.strip(), has_injection, flagged
