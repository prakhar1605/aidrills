This is what a vector database does, minus the index. Ten lines, no dependencies —
and it is asked constantly, because the interesting part is not the formula, it is
the three degenerate cases that produce `nan` in production and silently poison a
ranking.

Implement `cosine_top_k(query, vectors, k)`.

- Return the `k` nearest vectors as `(index, similarity)` pairs, most similar
  first. Ties break by the lower index.
- Cosine similarity is the dot product over the product of the norms.
- A zero vector has no direction. Its similarity is `0.0`, never `nan`. That
  applies to a zero query too.
- `k` larger than the corpus returns everything. `k <= 0` returns `[]`.
- An empty corpus returns `[]`.
- A vector whose length differs from the query raises `ValueError`.

```python
cosine_top_k([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]], k=2)
# [(0, 1.0), (1, 0.0)]
```

### What the interviewer is checking

The zero-vector guard, first and mostly. Empty documents and failed embeddings do
reach the index, and `0/0` propagates a `nan` that sorts unpredictably and quietly
corrupts every result above it. After that: whether you normalize once per vector
instead of recomputing norms inside a comparison, which is the difference between
this and something that melts on a real corpus.
