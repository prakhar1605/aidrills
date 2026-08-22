Loop over attempt numbers rather than counting failures. `for attempt in
range(1, max_attempts + 1)` with a `return fn()` inside the `try` makes the
success path fall out for free.
---
The wait after failure *n* is `min(max_delay, base_delay * 2 ** (n - 1))`. Note
the exponent is `n - 1`, so the first retry waits exactly `base_delay`. Then
multiply by `rand()` before handing it to `sleep`.
---
Two things to get exactly right. Catch only `(RateLimitError, ServerError)` and
let everything else escape untouched. And when `attempt == max_attempts`, `raise`
immediately — do not sleep first, or you add a pointless delay to every hard
failure.
