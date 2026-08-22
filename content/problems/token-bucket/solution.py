class TokenBucket:
    def __init__(self, capacity: float, refill_per_sec: float, now: float = 0.0) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_per_sec < 0:
            raise ValueError("refill_per_sec must not be negative")

        self.capacity = float(capacity)
        self.refill_per_sec = float(refill_per_sec)
        self._tokens = float(capacity)  # buckets start full
        self._updated = float(now)

    def _advance(self, now: float | None) -> None:
        """Lazy refill: nothing runs in the background, we just do the arithmetic."""
        if now is None:
            return
        # A clock that went backwards must not drain the bucket.
        elapsed = max(0.0, float(now) - self._updated)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_per_sec)
        self._updated = max(self._updated, float(now))

    @property
    def tokens(self) -> float:
        return self._tokens

    def consume(self, tokens: float = 1.0, now: float | None = None) -> bool:
        if tokens < 0:
            raise ValueError("cannot consume a negative number of tokens")
        self._advance(now)
        if tokens > self._tokens:
            return False  # a rejected request takes nothing
        self._tokens -= tokens
        return True

    def time_until(self, tokens: float, now: float | None = None) -> float:
        if tokens < 0:
            raise ValueError("cannot wait for a negative number of tokens")
        self._advance(now)
        if tokens <= self._tokens:
            return 0.0
        if tokens > self.capacity or self.refill_per_sec == 0:
            return float("inf")
        return (tokens - self._tokens) / self.refill_per_sec


# What the interviewer is checking:
#   - refill computed on demand from elapsed time, not on a timer
#   - min(capacity, ...) so an idle bucket does not accumulate an unbounded burst
#   - max(0.0, ...) on elapsed, and _updated never moving backwards
#   - the early return in consume() leaves the level untouched on failure
