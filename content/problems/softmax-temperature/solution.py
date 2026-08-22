import math


def softmax(logits: list[float], temperature: float = 1.0) -> list[float]:
    if temperature < 0:
        raise ValueError("temperature must not be negative")
    if not logits:
        return []

    if temperature == 0:
        # The limit as T -> 0 is one-hot on the argmax; max() already returns
        # the first maximum, so ties break toward the lower index.
        best = logits.index(max(logits))
        return [1.0 if i == best else 0.0 for i in range(len(logits))]

    scaled = [value / temperature for value in logits]
    top = max(scaled)
    exps = [math.exp(value - top) for value in scaled]
    total = sum(exps)
    return [value / total for value in exps]


# What the interviewer is checking:
#   - subtracting the max *after* scaling by temperature, not before; a small
#     temperature is exactly what blows the exponent up
#   - temperature == 0 handled as the limit rather than as an error
#   - the guard runs before the empty-list check, so softmax([], -1) still raises
