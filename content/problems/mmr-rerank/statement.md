Your top-5 chunks are five near-copies of the same paragraph, because the document
said the same thing five times and the embedding model agreed. You have burned the
context window on one fact. MMR is the standard fix: pick greedily, penalizing each
candidate by how much it looks like what you already picked.

Implement `mmr(query_sim, doc_sim, k, lambda_=0.5)`.

`query_sim[i]` is document *i*'s similarity to the query. `doc_sim[i][j]` is the
similarity between documents *i* and *j*. Return the selected indices, in the order
they were picked.

- The first pick is the most relevant document — the highest `query_sim`.
- Every pick after that maximizes, over the unselected documents,
  `lambda_ * query_sim[i] - (1 - lambda_) * max(doc_sim[i][j] for j in selected)`.
- Ties break toward the lower index, at every step.
- `k` larger than the corpus returns every document, still in MMR order.
  `k <= 0` returns `[]`. An empty corpus returns `[]`.
- `lambda_` outside `[0, 1]`, or a `doc_sim` that is not square and matching
  `query_sim`, raises `ValueError`.

### What the interviewer is checking

That the penalty is the **maximum** similarity to the selected set, not the mean.
The mean lets a candidate hide behind a large, diverse selection and is how people
accidentally reinvent plain relevance ranking. Then the seeding rule: the first pick
has an empty selected set, so it has to fall back to relevance rather than to
whatever an unguarded `max()` over nothing does. Expect "what does lambda mean to a
user?" — 1 is pure relevance, 0 is pure novelty, and 0.5 is where most systems land.
