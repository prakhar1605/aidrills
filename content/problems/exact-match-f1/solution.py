import re
import string
from collections import Counter

_PUNCT = str.maketrans("", "", string.punctuation)


def normalize_answer(text: str) -> str:
    text = text.lower()
    text = text.translate(_PUNCT)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def _tokens(text: str) -> list[str]:
    return normalize_answer(text).split()


def exact_match(pred: str, golds: list[str]) -> float:
    normalized = normalize_answer(pred)
    return float(any(normalized == normalize_answer(g) for g in golds))


def _f1(pred_tokens: list[str], gold_tokens: list[str]) -> float:
    if not pred_tokens or not gold_tokens:
        # Both empty is a match; exactly one empty is not.
        return float(pred_tokens == gold_tokens)

    # Counter & Counter keeps min(count) per token -- multiplicity, not a set.
    overlap = sum((Counter(pred_tokens) & Counter(gold_tokens)).values())
    if overlap == 0:
        return 0.0

    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def f1_score(pred: str, golds: list[str]) -> float:
    pred_tokens = _tokens(pred)
    return max((_f1(pred_tokens, _tokens(g)) for g in golds), default=0.0)


# What the interviewer is checking:
#   - Counter intersection rather than set intersection
#   - punctuation stripped *before* article removal, so "the," still matches
#   - the zero-overlap early return; without it precision and recall are both 0
#     and the harmonic mean divides by zero
#   - max over golds, not the first gold
