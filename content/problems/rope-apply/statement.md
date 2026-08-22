Llama, Mistral, Qwen, Gemma — all of them position tokens by rotating the query and
key vectors instead of adding a learned vector. RoPE is the reason context windows
can be extended after training, and it is a rotation matrix applied in pairs.

Implement two functions.

`rope_frequencies(dim, seq_len, base=10000.0)` returns `(cos, sin)`, each of shape
`(seq_len, dim // 2)`. The frequency for pair *i* is
`1 / base ** (2i / dim)`, and the angle at position *m* is `m` times that
frequency.

`apply_rope(x, cos, sin, offset=0)` rotates `x`, shape `(..., seq, dim)`. Treat the
last axis as `dim // 2` **adjacent pairs**: element `2i` and element `2i + 1`
rotate together by the angle for pair *i*.

```text
out[..., 2i]     = x[..., 2i] * cos_i - x[..., 2i+1] * sin_i
out[..., 2i + 1] = x[..., 2i] * sin_i + x[..., 2i+1] * cos_i
```

- `offset` is the absolute position of the first token in `x`, so a single decode
  step at position 7 uses row 7 of the tables.
- Leading batch and head axes must broadcast.
- An odd `dim` raises `ValueError`.
- `cos` and `sin` may be longer than the sequence; use the rows the offset selects.

### What the interviewer is checking

The property, not the formula: after rotation, the dot product between a query at
position *m* and a key at position *n* depends only on `m - n`. That is what makes
this a *relative* encoding despite being applied absolutely, and being able to say
it is most of the answer. Then the practical part — `offset`, because during
incremental decoding you rotate one token at a time and it has to land on the same
angle it would have had in a full forward pass.
