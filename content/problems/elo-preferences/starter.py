def expected_score(rating_a: float, rating_b: float) -> float:
    """A's expected result against B, between 0 and 1."""
    raise NotImplementedError


def elo_ratings(
    matches: list[dict],
    k: float = 32.0,
    initial: float = 1000.0,
) -> dict[str, float]:
    """Aggregate pairwise preferences into ratings.

    Args:
        matches: dicts with a, b and winner.
        k: how far one result moves a rating.
        initial: every player's starting rating.

    Returns:
        player -> final rating.

    Raises:
        ValueError: on an unknown winner or a player facing themselves.
    """
    raise NotImplementedError
