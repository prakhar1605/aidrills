An exact-match cache never hits, because nobody types the same question twice.
"What's your refund policy?" and "how do refunds work" are the same request with a
0% string overlap and a 0.94 cosine. Caching on the embedding is the cheapest
latency and cost win in most LLM products — and the most dangerous, because a
threshold set too low serves the wrong answer confidently.

Implement `SemanticCache`.

`SemanticCache(threshold=0.9, max_size=None)`

- `get(vector)` — return the value of the most similar entry whose cosine
  similarity is at least `threshold`, or `None`. A hit counts as a use.
- `put(vector, value)` — store it. If an existing entry is already within
  `threshold` of this vector, **update that entry** rather than adding a near-copy.
- `len(cache)` — how many entries are stored.
- `stats` — a dict with `hits` and `misses`, counted by `get`.
- With `max_size` set, evict the **least recently used** entry when full. Both a
  hit and a `put` count as a use. `max_size=None` is unbounded.
- A zero vector has no direction: similarity `0.0`, never `nan`.
- `threshold` outside `[0, 1]`, a `max_size` below 1, or a vector whose dimension
  disagrees with what is stored, raises `ValueError`.

### What the interviewer is checking

The update rule. Without it, a cache under a stream of paraphrases fills with
near-identical entries, and the eviction policy starts throwing away the *distinct*
ones — the cache gets bigger, slower and less useful at the same time. Then LRU
bookkeeping on reads as well as writes. The real conversation afterwards is the
threshold: it is a precision/recall dial where the cost of a false positive is
answering the wrong question, so ask what happens at 0.85.
