Every corpus has the same paragraph forty times: a boilerplate footer, a legal
notice, a doc page that got copied between products. Indexed as-is, it wins
retrieval for half your queries. Exact hashing misses it, because one copy has a
different date in it.

Implement three functions.

`shingles(text, n=5)` — the set of overlapping character n-grams of `text`,
lowercased with runs of whitespace collapsed to one space. Text shorter than `n`
after normalizing gives a single shingle: the whole string. Empty text gives an
empty set.

`jaccard(a, b)` — intersection over union of two sets. Two empty sets are
identical, so that is `1.0`, not a division by zero.

`dedupe(texts, threshold=0.8, n=5)` — return the indices to **keep**, ascending.
Walk the list in order; keep a text if its Jaccard similarity against every already
kept text is below `threshold`. First occurrence wins.

- `threshold` outside `[0, 1]` raises `ValueError`.
- An empty list returns `[]`.
- Exact duplicates are dropped at any threshold above 0.

### What the interviewer is checking

Two things people get wrong under time pressure. `0/0` in the Jaccard, which is a
real case as soon as an empty chunk reaches the deduper. And comparing against the
*kept* set rather than all previous texts — otherwise a chain of three chunks, each
similar to the last but not to the first, quietly drops the middle one and keeps the
third. Expect "this is quadratic, now do a million chunks": the answer is MinHash
and LSH, and knowing that is the point of the follow-up.
