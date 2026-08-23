import re

PLACEHOLDERS = {
    "email": "[EMAIL]",
    "api_key": "[API_KEY]",
    "credit_card": "[CREDIT_CARD]",
    "ssn": "[SSN]",
    "ip": "[IP]",
    "phone": "[PHONE]",
}


def luhn(digits: str) -> bool:
    """True if `digits` passes the Luhn checksum."""
    raise NotImplementedError


def redact(text: str, types: list[str] | None = None) -> tuple[str, dict]:
    """Replace personal data with placeholders.

    Args:
        text: the text to scrub.
        types: which types to scan for; None means all of them.

    Returns:
        (redacted_text, counts) where counts covers every scanned type.

    Raises:
        ValueError: on an unknown type name.
    """
    raise NotImplementedError
