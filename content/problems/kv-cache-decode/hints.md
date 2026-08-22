Store the cache as two arrays and grow them with `np.concatenate`. Everything
else — length, eviction, reset — is one line on top of that.
---
`decode_step` is: append, then softmax over `keys @ q / sqrt(dim)`, then weight
the values. Note the ordering — the new key has to be in the cache before you
score, or the token cannot attend to itself.
---
Two details decide this problem. Copy in `append`, because callers reuse the same
`(1, dim)` buffer every step and a stored reference silently rewrites history.
And evict with `self._keys[-max_len:]`, keeping the newest — the window slides
forward, it does not truncate.
