import re
import string
from collections import Counter


def normalize_answer(text: str) -> str:
    """Lowercase, drop punctuation and articles, collapse whitespace."""
    raise NotImplementedError


def exact_match(pred: str, golds: list[str]) -> float:
    """1.0 if the normalized prediction matches any normalized gold."""
    raise NotImplementedError


def f1_score(pred: str, golds: list[str]) -> float:
    """Token-level F1 against the best-matching gold answer."""
    raise NotImplementedError
