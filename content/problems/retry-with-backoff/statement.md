Every LLM provider will 429 you, usually all at once, usually in production. The
retry wrapper is the single most-written piece of code in LLM plumbing and the
single most-often-wrong: no cap, no jitter, and retrying errors that will never
succeed.

Implement `call_with_retry(fn, max_attempts=4, base_delay=0.5, max_delay=8.0, sleep=time.sleep, rand=random.random)`.

- Call `fn()`. On success, return its result.
- Retry only `RateLimitError` and `ServerError` from `mock_llm`. Any other
  exception propagates immediately, with no sleep.
- After the *n*-th failure (1-indexed) the base wait is
  `min(max_delay, base_delay * 2 ** (n - 1))`.
- Apply **full jitter**: the actual wait is `base_wait * rand()`. Sleep by calling
  `sleep(wait)` — never `time.sleep` directly, so it is testable.
- Give up after `max_attempts` calls and re-raise the last exception unchanged.
  There is no sleep after the final failure.

`sleep` and `rand` are injected so tests can drive it: `rand=lambda: 1.0` makes the
delays exactly the un-jittered schedule.

### What the interviewer is checking

Three things, in order of how often they are missed. **Full jitter, not fixed
backoff** — without it every client that got rate-limited retries at the same
instant and re-creates the stampede. **The cap**, or attempt 10 sleeps for four
minutes. And **retrying only what is retryable** — a 400 for a malformed request
will 400 forever, and burning four attempts on it just turns a fast failure into a
slow one.
