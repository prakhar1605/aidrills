import math


def bm25_scores(
    corpus: list[list[str]],
    query: list[str],
    k1: float = 1.5,
    b: float = 0.75,
) -> list[float]:
    """Score every document in `corpus` against `query` with Okapi BM25.

    Args:
        corpus: tokenized documents.
        query: tokenized query; duplicates count more than once.
        k1: term-frequency saturation.
        b: length-normalization strength, 0.0 disables it.

    Returns:
        One float per document, in corpus order.
    """
    raise NotImplementedError
