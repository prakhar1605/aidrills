import math


def _cosine(a: list[float], b: list[float]) -> float:
    norm_a = math.sqrt(sum(value * value for value in a))
    norm_b = math.sqrt(sum(value * value for value in b))
    # A zero vector points nowhere; the angle is undefined, so report no
    # similarity rather than letting 0/0 become nan.
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


def cosine_top_k(
    query: list[float],
    vectors: list[list[float]],
    k: int = 5,
) -> list[tuple[int, float]]:
    for index, vector in enumerate(vectors):
        if len(vector) != len(query):
            raise ValueError(
                f"vector {index} has length {len(vector)}, expected {len(query)}"
            )

    if k <= 0 or not vectors:
        return []

    scored = [(index, _cosine(query, vector)) for index, vector in enumerate(vectors)]
    # -score for descending, index ascending to break ties toward the lower one.
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored[:k]


# What the interviewer is checking:
#   - the zero-norm guard on *both* sides
#   - validation runs over the whole corpus before any scoring, so a bad vector
#     is reported rather than silently ranked
#   - an explicit tie-break instead of relying on sort stability
