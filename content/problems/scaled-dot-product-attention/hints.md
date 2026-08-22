Do it in four statements: scores, mask, softmax, output. Resist writing any
Python loop — every step is one numpy call.
---
`np.matmul` already batches over leading axes. To transpose only the last two,
use `np.swapaxes(K, -1, -2)`; plain `.T` reverses *all* axes and silently
corrupts anything with a batch dimension.
---
Mask with `np.where(mask, scores, -np.inf)` before the softmax so the masked
entries exponentiate to exactly zero and the surviving weights renormalize on
their own. Then subtract `np.max(scores, axis=-1, keepdims=True)` — `keepdims`
is what makes the broadcast line up.
