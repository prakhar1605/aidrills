def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def shingles(text: str, n: int = 5) -> set[str]:
    if n <= 0:
        raise ValueError("n must be positive")
    normalized = _normalize(text)
    if not normalized:
        return set()
    if len(normalized) <= n:
        # Too short to slide a window over -- the whole string is the shingle.
        return {normalized}
    return {normalized[i : i + n] for i in range(len(normalized) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0  # identical, not 0/0
    union = len(a | b)
    if union == 0:
        return 1.0
    return len(a & b) / union


def dedupe(texts: list[str], threshold: float = 0.8, n: int = 5) -> list[int]:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0, 1], got {threshold}")

    kept: list[int] = []
    kept_shingles: list[set[str]] = []

    for index, text in enumerate(texts):
        current = shingles(text, n)
        # Compare against what survived, not against everything seen -- a chain
        # of gradual edits should not drop links out of the middle.
        if any(jaccard(current, other) >= threshold for other in kept_shingles):
            continue
        kept.append(index)
        kept_shingles.append(current)

    return kept


# What the interviewer is checking:
#   - normalization before shingling, so whitespace and case are not the thing
#     being compared
#   - the empty/empty case in jaccard
#   - shingles cached per kept text; recomputing them inside the inner loop turns
#     an O(n^2) comparison into an O(n^2 * len(text)) one
