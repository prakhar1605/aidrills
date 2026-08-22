class TokenBucket:
    """Allows a burst up to `capacity`, then a steady `refill_per_sec`."""

    def __init__(self, capacity: float, refill_per_sec: float, now: float = 0.0) -> None:
        """
        Raises:
            ValueError: on a non-positive capacity or a negative refill rate.
        """
        raise NotImplementedError

    @property
    def tokens(self) -> float:
        """The level at the last observed time."""
        raise NotImplementedError

    def consume(self, tokens: float = 1.0, now: float | None = None) -> bool:
        """Take `tokens` if they are available. A failure takes nothing."""
        raise NotImplementedError

    def time_until(self, tokens: float, now: float | None = None) -> float:
        """Seconds until `tokens` are available; inf if that can never happen."""
        raise NotImplementedError
