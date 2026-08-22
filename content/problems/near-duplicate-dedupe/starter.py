def shingles(text: str, n: int = 5) -> set[str]:
    """Overlapping character n-grams of the normalized text."""
    raise NotImplementedError


def jaccard(a: set[str], b: set[str]) -> float:
    """Intersection over union; two empty sets score 1.0."""
    raise NotImplementedError


def dedupe(texts: list[str], threshold: float = 0.8, n: int = 5) -> list[int]:
    """Indices of the texts to keep, first occurrence winning.

    Raises:
        ValueError: if threshold is outside [0, 1].
    """
    raise NotImplementedError
