def mmr(
    query_sim: list[float],
    doc_sim: list[list[float]],
    k: int,
    lambda_: float = 0.5,
) -> list[int]:
    """Greedily select k documents balancing relevance against redundancy.

    Args:
        query_sim: similarity of each document to the query.
        doc_sim: pairwise document-document similarity, n x n.
        k: how many to select.
        lambda_: 1.0 is pure relevance, 0.0 is pure diversity.

    Returns:
        Selected indices, in selection order.

    Raises:
        ValueError: on a bad lambda_ or a malformed doc_sim.
    """
    raise NotImplementedError
