You never need the original scores. Two dictionaries are enough: accumulated
fused score per id, and the best rank that id ever achieved.
---
Iterate each ranking with `enumerate(ranking, start=1)` so ranks are 1-indexed,
and add `1 / (k + rank)` into the running total. Track a `seen` set per ranking
so a repeated id inside one list only counts once.
---
Sort with a tuple key: `(-score, best_rank, doc_id)`. Negating the score gives
descending order while the two tie-breakers stay ascending, and it makes the
result independent of insertion order.
