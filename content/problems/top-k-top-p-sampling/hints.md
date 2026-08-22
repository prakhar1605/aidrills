Do not filter the list in place and do not sort it. Work with *indices* — sort
`range(len(logits))` by score — so you can write the mask back into the original
positions at the end.
---
top-k is a set of surviving indices. top-p then operates only on that set:
softmax those logits, renormalized over the survivors, and walk them in
descending probability accumulating the mass.
---
Put the `break` after you add the token and after you add its probability, so a
distribution whose first token already exceeds `top_p` still keeps that token.
And subtract `max(values)` before `math.exp` — `exp(900)` raises OverflowError.
