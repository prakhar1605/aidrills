import math


def cosine_top_k(
    query: list[float],
    vectors: list[list[float]],
    k: int = 5,
) -> list[tuple[int, float]]:
    """Rank `vectors` by cosine similarity to `query`.

    Args:
        query: the query embedding.
        vectors: the corpus embeddings.
        k: how many results to return.

    Returns:
        (index, similarity) pairs, most similar first.

    Raises:
        ValueError: if any vector has a different length from the query.
    """
    raise NotImplementedError
