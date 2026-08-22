The mask has to appear twice: once to zero out the padded embeddings, and once to
count how many tokens you actually summed. Anything that uses it only once is
the bug this problem is about.
---
Broadcast the mask to `(batch, seq, 1)` with `mask[..., None]`, multiply, then
`sum(axis=1)` both the products and the mask itself. The quotient is the pooled
vector.
---
Guard the division before it happens: `np.where(counts == 0, 1.0, counts)` as
the divisor, then `np.where(counts == 0, 0.0, pooled)` for the result. Fixing
`nan` after the fact still trips a RuntimeWarning, and in `normalize` the same
pattern handles the zero vector.
