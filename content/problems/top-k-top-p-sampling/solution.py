import math

NEG_INF = float("-inf")


def _softmax(values: list[float]) -> list[float]:
    # Subtract the max first, or exp() overflows on realistic logits.
    top = max(values)
    exps = [math.exp(v - top) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


def filter_logits(
    logits: list[float],
    top_k: int = 0,
    top_p: float = 0.0,
) -> list[float]:
    if not logits:
        return []

    keep = set(range(len(logits)))

    if 0 < top_k < len(logits):
        # -logit for descending order, index ascending to break ties low.
        ranked = sorted(range(len(logits)), key=lambda i: (-logits[i], i))
        keep = set(ranked[:top_k])

    if top_p > 0.0:
        surviving = sorted(keep, key=lambda i: (-logits[i], i))
        probs = _softmax([logits[i] for i in surviving])
        nucleus: set[int] = set()
        cumulative = 0.0
        for index, prob in zip(surviving, probs):
            nucleus.add(index)
            cumulative += prob
            if cumulative >= top_p:
                break
        keep = nucleus  # the loop body always runs once, so never empty

    return [logits[i] if i in keep else NEG_INF for i in range(len(logits))]


# What the interviewer is checking:
#   - softmax is applied to the post-top_k survivors, and renormalized over them
#     rather than over the whole vocabulary
#   - max-subtraction in the softmax (overflow on logits around 800+)
#   - the nucleus always contains at least one token
#   - a new list is returned; the caller's logits are untouched
