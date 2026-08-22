import math
from typing import Any


class SemanticCache:
    """A cache keyed by embedding similarity rather than exact match."""

    def __init__(self, threshold: float = 0.9, max_size: int | None = None) -> None:
        """
        Raises:
            ValueError: on a threshold outside [0, 1] or a max_size below 1.
        """
        raise NotImplementedError

    def get(self, vector: list[float]) -> Any | None:
        """The value of the closest entry within `threshold`, or None."""
        raise NotImplementedError

    def put(self, vector: list[float], value: Any) -> None:
        """Store `value`, updating a near-identical entry instead of adding one."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    @property
    def stats(self) -> dict:
        """Counts of hits and misses."""
        raise NotImplementedError
