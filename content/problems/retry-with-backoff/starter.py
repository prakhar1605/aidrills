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
    """Call `fn`, retrying rate-limit and server errors with jittered backoff.

    Args:
        fn: zero-argument callable to invoke.
        max_attempts: total calls, including the first.
        base_delay: seconds before the first retry.
        max_delay: ceiling on the un-jittered wait.
        sleep: injected sleeper, called with the wait in seconds.
        rand: injected source of randomness in [0, 1).

    Returns:
        Whatever `fn` returns.

    Raises:
        The last exception, once the attempts are exhausted.
    """
    raise NotImplementedError
