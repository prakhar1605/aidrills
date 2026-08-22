import math


def filter_logits(
    logits: list[float],
    top_k: int = 0,
    top_p: float = 0.0,
) -> list[float]:
    """Mask out logits that top-k / top-p sampling would never draw.

    Args:
        logits: raw, unnormalized scores over the vocabulary.
        top_k: keep the k highest logits; 0 disables.
        top_p: keep the smallest nucleus reaching this probability mass;
            0.0 disables.

    Returns:
        A new list where rejected positions are float("-inf").
    """
    raise NotImplementedError
