import random
import re
import string


def normalize(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace."""
    raise NotImplementedError


def dedupe_and_split(
    examples: list[dict],
    ratios: tuple[float, float, float] = (0.8, 0.1, 0.1),
    seed: int = 0,
) -> dict:
    """Remove duplicate texts, then split deterministically into three sets.

    Args:
        examples: dicts with a text field.
        ratios: train, val and test shares; must sum to 1.0.
        seed: shuffle seed.

    Returns:
        train, val, test and the number of duplicates dropped.

    Raises:
        ValueError: on malformed ratios.
    """
    raise NotImplementedError
