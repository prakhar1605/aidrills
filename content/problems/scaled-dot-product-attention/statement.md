The whiteboard question. Write attention in numpy, no framework, and be ready to
justify every line — especially the division by the square root of the head
dimension.

Implement `attention(Q, K, V, mask=None)` returning the tuple
`(output, weights)`.

- `Q` has shape `(..., n_q, d_k)`, `K` has shape `(..., n_k, d_k)`,
  `V` has shape `(..., n_k, d_v)`. Leading batch or head axes must broadcast.
- Scores are `Q @ K.T / sqrt(d_k)`, transposing only the last two axes.
- `mask` is a boolean array broadcastable to the scores, where **False means "do
  not attend"**. Masked scores become `-inf` before the softmax.
- The softmax runs over the last axis and must be numerically stable — subtract
  the row max before exponentiating.
- `weights` has the shape of the scores and each row sums to 1.
- `output` is `weights @ V`, shape `(..., n_q, d_v)`.

Assume every row leaves at least one position unmasked.

### What the interviewer is checking

Why `sqrt(d_k)`: for random Q and K with unit-variance entries the dot product has
variance `d_k`, so without the scaling the softmax saturates as the head grows and
gradients vanish. Then: the transpose has to be `swapaxes(-1, -2)`, not `.T`, or
batched inputs silently produce garbage. And a causal mask is the immediate
follow-up, so expect to be asked for it.
