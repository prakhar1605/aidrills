SCORES = {"a": 1.0, "b": 0.0, "tie": 0.5}


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def elo_ratings(
    matches: list[dict],
    k: float = 32.0,
    initial: float = 1000.0,
) -> dict[str, float]:
    ratings: dict[str, float] = {}

    for match in matches:
        a, b, winner = match["a"], match["b"], match["winner"]
        if a == b:
            raise ValueError(f"player {a!r} cannot play itself")
        if winner not in SCORES:
            raise ValueError(f"winner must be 'a', 'b' or 'tie', got {winner!r}")

        ratings.setdefault(a, float(initial))
        ratings.setdefault(b, float(initial))

        # Snapshot both ratings first. Updating in place and then computing the
        # second expectation destroys the zero-sum property.
        before_a, before_b = ratings[a], ratings[b]
        score_a = SCORES[winner]

        ratings[a] = before_a + k * (score_a - expected_score(before_a, before_b))
        ratings[b] = before_b + k * ((1.0 - score_a) - expected_score(before_b, before_a))

    return ratings


# What the interviewer is checking:
#   - the pre-match snapshot, which is what keeps the total rating constant
#   - a scores table rather than a chain of ifs, so "tie" cannot be forgotten
#   - setdefault, so a player who only ever loses still appears in the output
#   - validation before mutation, so a bad record does not half-apply
