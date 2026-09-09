import re
import html
from typing import Optional

# Injection guard patterns
SUSPICIOUS_PROMPT_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*:\s*you\s+are",
    r"disregard\s+the\s+above",
    r"<script.*?>",
    r"javascript:",
    r"base64,",
]

def sanitize_user_input(text: str, max_length: int = 5000) -> str:
    """Sanitizes user input by escaping HTML tags, trimming whitespace, and validating against prompt injection attempts."""
    if not text:
        return ""

    # Truncate to maximum allowed length
    truncated = text.strip()[:max_length]

    # Escape HTML special characters
    escaped = html.escape(truncated)

    # Check for obvious jailbreak/injection patterns and neutralize
    for pattern in SUSPICIOUS_PROMPT_PATTERNS:
        escaped = re.sub(pattern, "[FILTERED_INPUT]", escaped, flags=re.IGNORECASE)

    return escaped

def sanitize_filename(filename: str) -> str:
    """Removes unsafe characters and directory traversal attempts from filenames."""
    clean = filename.replace("..", "").replace("/", "_").replace("\\", "_")
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean)
    clean = re.sub(r"_+", "_", clean)
    return clean.strip("_")[:100]

