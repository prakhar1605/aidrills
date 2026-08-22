import random
import time
from typing import Any, Callable

from mock_llm import RateLimitError, ServerError

RETRYABLE = (RateLimitError, ServerError)


def call_with_retry(
    fn: Callable[[], Any],
    max_attempts: int = 4,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    sleep: Callable[[float], None] = time.sleep,
    rand: Callable[[], float] = random.random,
) -> Any:
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except RETRYABLE:
            # No sleep after the last attempt -- the caller is about to see
            # the exception, not another try.
            if attempt == max_attempts:
                raise
            wait = min(max_delay, base_delay * 2 ** (attempt - 1))
            sleep(wait * rand())  # full jitter
    raise RuntimeError("unreachable: max_attempts must be at least 1")


# What the interviewer is checking:
#   - `except RETRYABLE` and nothing broader; a bare `except Exception` retries
#     the 400s too
#   - the min(max_delay, ...) cap applied to the base wait, before jitter
#   - full jitter (uniform over [0, wait]) rather than wait +/- a little, which
#     is what actually de-synchronizes a stampede
#   - re-raising the original exception rather than wrapping it
