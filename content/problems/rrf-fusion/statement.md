You have a BM25 ranking and a vector ranking of the same corpus. Their scores are
not comparable — one is a log-odds-ish sum, the other a cosine. Normalizing them
onto a shared scale is fiddly and brittle. Reciprocal Rank Fusion sidesteps the
whole problem by throwing the scores away and keeping only the ranks.

Implement `rrf_fuse(rankings, k=60, top_n=None)`.

`rankings` is a list of ranked lists of document ids, best-first. Score each
document by summing `1 / (k + rank)` over every list it appears in, where `rank` is
1-indexed. Return the ids sorted by descending score.

- A document missing from a list simply contributes nothing from that list.
- If an id appears more than once within a single list, only its best (lowest)
  rank in that list counts.
- Ties: break by the best rank the document reached in any list (lower first),
  then by id ascending. Fusion must be deterministic.
- `top_n=None` returns everything; otherwise return the first `top_n`.
- No rankings, or only empty rankings, returns `[]`.

```python
rrf_fuse([["a", "b", "c"], ["c", "a", "d"]], k=1)
# a: 1/2 + 1/3 = .833   c: 1/4 + 1/2 = .75   b: 1/3   d: 1/4
# ["a", "c", "b", "d"]
```

### What the interviewer is checking

That you can explain `k`. It damps the top of each list: with `k=60` the gap
between rank 1 and rank 2 is small, so a document has to do well in *several*
rankings to climb — which is the entire point. A small `k` lets one retriever's
favourite dominate. The other thing they watch for is whether you made ties
deterministic without being asked.
