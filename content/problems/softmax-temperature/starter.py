import math


def softmax(logits: list[float], temperature: float = 1.0) -> list[float]:
    """Turn logits into a probability distribution.

    Args:
        logits: raw, unnormalized scores.
        temperature: sharpening factor; 0.0 means greedy.

    Returns:
        Probabilities summing to 1.0, same length as `logits`.

    Raises:
        ValueError: if temperature is negative.
    """
    raise NotImplementedError
