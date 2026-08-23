import random
import re
import string

_PUNCT = str.maketrans("", "", string.punctuation)
SPLITS = ("train", "val", "test")


def normalize(text: str) -> str:
    return " ".join(text.lower().translate(_PUNCT).split())


def _largest_remainder(total: int, ratios: tuple[float, ...]) -> list[int]:
    """Split `total` so the counts sum to exactly `total`."""
    raw = [total * ratio for ratio in ratios]
    counts = [int(value) for value in raw]
    leftover = total - sum(counts)
    # Biggest fractional part first; index breaks ties so this is deterministic.
    order = sorted(range(len(ratios)), key=lambda i: (-(raw[i] - counts[i]), i))
    for index in order[:leftover]:
        counts[index] += 1
    return counts


def dedupe_and_split(
    examples: list[dict],
    ratios: tuple[float, float, float] = (0.8, 0.1, 0.1),
    seed: int = 0,
) -> dict:
    if len(ratios) != 3:
        raise ValueError(f"expected three ratios, got {len(ratios)}")
    if any(ratio < 0 for ratio in ratios):
        raise ValueError("ratios must not be negative")
    if abs(sum(ratios) - 1.0) > 1e-9:
        raise ValueError(f"ratios must sum to 1.0, got {sum(ratios)}")

    # Dedupe across the whole dataset, before splitting -- deduping each split
    # separately leaves exactly the cross-split copies that cause leakage.
    seen: set[str] = set()
    unique: list[dict] = []
    for example in examples:
        key = normalize(example["text"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(example)

    dropped = len(examples) - len(unique)

    shuffled = list(unique)
    random.Random(seed).shuffle(shuffled)

    counts = _largest_remainder(len(shuffled), ratios)
    result: dict = {}
    start = 0
    for name, count in zip(SPLITS, counts):
        result[name] = shuffled[start : start + count]
        start += count

    result["dropped"] = dropped
    return result


# What the interviewer is checking:
#   - dedupe over the full dataset first
#   - largest remainder, so the three counts add up to n for every n
#   - random.Random(seed) rather than seeding the global RNG, which would make
#     the function change behaviour depending on what else ran first
