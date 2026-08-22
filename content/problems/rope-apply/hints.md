Do not loop over pairs. `x[..., 0::2]` and `x[..., 1::2]` give you the two halves
of every pair as strided views, and the whole rotation is two expressions over
them.
---
`cos` and `sin` have shape `(seq, dim // 2)`, and the halves you sliced have
shape `(..., seq, dim // 2)`. Those broadcast directly, so batch and head axes
never need to be mentioned.
---
Write the results back with the same strided slices — `out[..., 0::2] = ...` and
`out[..., 1::2] = ...` — into an array you allocated with `np.empty_like`.
Slice the tables with `cos[offset : offset + seq]` so a one-token decode step at
position 7 uses row 7.
