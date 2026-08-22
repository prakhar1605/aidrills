The other half of the 429 problem: instead of reacting to the provider's limit,
stay under it. A token bucket allows a burst up to its capacity and a steady rate
after that, which is exactly the shape LLM APIs sell — and unlike a fixed window it
does not let you send two windows' worth of traffic across a boundary.

Implement `TokenBucket`.

`TokenBucket(capacity, refill_per_sec, now=0.0)` starts **full**. Time is passed in
rather than read from the clock, so this is testable.

- `consume(tokens=1.0, now=None)` — refill for the time elapsed since the last
  observation, capped at `capacity`, then take the tokens if they are there.
  Returns `True` on success, `False` otherwise, and takes nothing when it fails.
- `tokens` — the level at the last observed time.
- `time_until(tokens, now=None)` — seconds until that many tokens are available.
  `0.0` if they already are; `float("inf")` if the request can never be satisfied.
- `now=None` means "no time has passed since the last observation".
- A `now` earlier than the last observation must not drain or rewind the bucket.
  Clocks go backwards.
- `capacity <= 0`, a negative `refill_per_sec`, or a negative request raises
  `ValueError`.
- A request larger than `capacity` can never succeed.

### What the interviewer is checking

Lazy refill. Candidates reach for a background thread or a timer; the bucket only
needs to know the elapsed time at the moment someone asks, which makes it a couple
of floats and no concurrency. Then the two clamps — refill capped at capacity, and
elapsed time floored at zero — and the rule that a failed `consume` is a no-op,
because a limiter that leaks tokens on rejection starves every caller it rejects.
