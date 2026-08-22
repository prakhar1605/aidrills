import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    """Pull the first JSON object or array out of an LLM response.

    Args:
        text: raw model output, possibly fenced and surrounded by prose.

    Returns:
        The decoded value, or None if nothing parseable was found.
    """
    raise NotImplementedError
