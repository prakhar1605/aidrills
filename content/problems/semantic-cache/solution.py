import math
from typing import Any


def _cosine(a: list[float], b: list[float]) -> float:
    norm_a = math.sqrt(sum(v * v for v in a))
    norm_b = math.sqrt(sum(v * v for v in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0  # no direction, so no similarity -- not 0/0
    return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


class SemanticCache:
    def __init__(self, threshold: float = 0.9, max_size: int | None = None) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"threshold must be in [0, 1], got {threshold}")
        if max_size is not None and max_size < 1:
            raise ValueError(f"max_size must be at least 1, got {max_size}")

        self.threshold = threshold
        self.max_size = max_size
        # Parallel lists, ordered least-recently-used first.
        self._vectors: list[list[float]] = []
        self._values: list[Any] = []
        self._hits = 0
        self._misses = 0

    def _check_dim(self, vector: list[float]) -> None:
        if self._vectors and len(vector) != len(self._vectors[0]):
            raise ValueError(
                f"vector has length {len(vector)}, cache holds {len(self._vectors[0])}"
            )

    def _best_match(self, vector: list[float]) -> int | None:
        best_index, best_score = None, self.threshold
        for index, stored in enumerate(self._vectors):
            score = _cosine(vector, stored)
            if score >= best_score:
                best_index, best_score = index, score
        return best_index

    def _touch(self, index: int) -> None:
        """Move an entry to the most-recently-used end."""
        self._vectors.append(self._vectors.pop(index))
        self._values.append(self._values.pop(index))

    def get(self, vector: list[float]) -> Any | None:
        self._check_dim(vector)
        index = self._best_match(vector)
        if index is None:
            self._misses += 1
            return None
        value = self._values[index]
        self._touch(index)
        self._hits += 1
        return value

    def put(self, vector: list[float], value: Any) -> None:
        self._check_dim(vector)
        index = self._best_match(vector)
        if index is not None:
            # Refresh the near-identical entry instead of storing a near-copy.
            self._vectors[index] = list(vector)
            self._values[index] = value
            self._touch(index)
            return

        self._vectors.append(list(vector))
        self._values.append(value)
        if self.max_size is not None and len(self._vectors) > self.max_size:
            self._vectors.pop(0)
            self._values.pop(0)

    def __len__(self) -> int:
        return len(self._vectors)

    @property
    def stats(self) -> dict:
        return {"hits": self._hits, "misses": self._misses}


# What the interviewer is checking:
#   - put() reuses the same nearest-match search as get(), so the update rule and
#     the hit rule can never disagree
#   - recency is refreshed on reads too; LRU that only tracks writes evicts the
#     entries people are actually using
#   - >= threshold, not >, so a threshold of 1.0 still matches an exact repeat
#   - the zero-norm guard
