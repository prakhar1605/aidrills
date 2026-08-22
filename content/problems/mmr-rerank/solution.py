def mmr(
    query_sim: list[float],
    doc_sim: list[list[float]],
    k: int,
    lambda_: float = 0.5,
) -> list[int]:
    if not 0.0 <= lambda_ <= 1.0:
        raise ValueError(f"lambda_ must be in [0, 1], got {lambda_}")

    n = len(query_sim)
    if len(doc_sim) != n or any(len(row) != n for row in doc_sim):
        raise ValueError(f"doc_sim must be {n}x{n}")

    if k <= 0 or n == 0:
        return []

    remaining = list(range(n))
    # Seed with pure relevance: with nothing selected there is no redundancy to
    # penalize, and max() over an empty set has no answer.
    first = min(remaining, key=lambda i: (-query_sim[i], i))
    selected = [first]
    remaining.remove(first)

    while remaining and len(selected) < k:
        best = min(
            remaining,
            key=lambda i: (
                -(
                    lambda_ * query_sim[i]
                    - (1 - lambda_) * max(doc_sim[i][j] for j in selected)
                ),
                i,
            ),
        )
        selected.append(best)
        remaining.remove(best)

    return selected


# What the interviewer is checking:
#   - max(), not mean(), over the selected set
#   - the first pick is seeded separately
#   - min() on a (-score, index) tuple gives "highest score, lowest index" in one
#     expression, so ties are total rather than left to sort stability
#   - validation of lambda_ and the matrix shape before any selection happens
