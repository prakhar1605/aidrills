Generating a token needs attention over every previous token, and recomputing those
keys and values each step makes decoding quadratic. The cache is the fix, it is
where most of your inference memory goes, and a sliding window is the cheapest way
to bound it.

Implement `KVCache` and `decode_step`.

`KVCache(max_len=None)`

- `append(k, v)` — `k` and `v` have shape `(n_new, dim)`. Store a **copy**; the
  caller may reuse its buffers.
- `keys` and `values` — the cached rows, oldest first, shape `(length, dim)`.
- `len(cache)` — how many positions are cached.
- `reset()` — empty it.
- With `max_len` set, the cache holds at most that many positions and drops the
  oldest first. `max_len=None` is unbounded.
- Before the first append, `len(cache)` is `0`.

`decode_step(q, k_new, v_new, cache)`

Append the new key and value, then attend `q` — shape `(dim,)`, one token — over
everything in the cache. Scaled dot-product with a numerically stable softmax, same
as a full forward pass. Return the output vector, shape `(dim_v,)`.

### What the interviewer is checking

That step *t* of incremental decoding produces exactly what a full pass over the
whole prefix would. That equivalence is the entire justification for the cache, and
if your indexing is off by one it still runs and still emits plausible text. Then
the defensive copy in `append`, and the eviction order — dropping the *newest* rows
under a window is a bug that only shows up on long inputs.
