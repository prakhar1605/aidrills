Sentence-transformers is a mean over token embeddings and an L2 normalize. That is
the whole trick. The bug that gets shipped is pooling over the padding as well as
the tokens, which quietly makes every short document in a batch drift toward the
same vector — retrieval gets worse and nothing errors.

Implement two functions.

`mean_pool(token_embeddings, attention_mask)` — `token_embeddings` has shape
`(batch, seq, dim)`, `attention_mask` has shape `(batch, seq)` where 1 marks a real
token and 0 marks padding. Return `(batch, dim)`: the mean over the real tokens
only.

`normalize(vectors)` — L2-normalize each row of a `(batch, dim)` array to unit
length.

- A row whose mask is all zeros has nothing to average. Return zeros for it, not
  `nan`.
- A zero row in `normalize` stays zero, not `nan`.
- Neither function mutates its inputs.
- The mask may arrive as ints or floats.

### What the interviewer is checking

Whether you multiply by the mask *and* divide by the mask sum, rather than
`embeddings.mean(axis=1)`. Then the empty-row guard, which is the same `0/0`
problem in a different costume. The follow-up is usually "why normalize?" — because
cosine similarity on unnormalized vectors is a dot product divided by norms every
single time you compare, and normalizing once at index time makes it one matmul.
