`get` and `put` both need "the closest stored entry within the threshold".
Write that search once and call it from both — that is what keeps the update rule
consistent with the hit rule.
---
Two parallel lists ordered least-recently-used first are enough. A "use" is:
pop the entry out and append it back at the end. Eviction is then `pop(0)`.
---
Compare with `>=` so a threshold of 1.0 still matches an identical vector, and
guard the zero-norm case before dividing. Refresh recency on a cache *hit*, not
just on writes — otherwise the entries getting all the traffic are the first ones
evicted.
