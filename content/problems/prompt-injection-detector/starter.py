import re

WEIGHTS = {
    "instruction_override": 0.5,
    "system_prompt_exfil": 0.4,
    "role_switch": 0.3,
    "delimiter_injection": 0.3,
    "encoded_payload": 0.2,
    "urgency_override": 0.15,
}


def detect_injection(text: str) -> dict:
    """Score `text` for prompt-injection signals.

    Args:
        text: untrusted content -- a retrieved document, a tool result, a form field.

    Returns:
        A dict with "signals" (sorted list of ids), "score" (0.0-1.0) and
        "flagged" (score >= 0.5).
    """
    raise NotImplementedError
