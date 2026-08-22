Write the three special cases first — negative temperature, zero temperature,
empty list — and the general path becomes four unremarkable lines.
---
Scale by temperature first, then do a stable softmax on the scaled values:
subtract the maximum, exponentiate, divide by the sum.
---
Order matters: `max()` must be taken on the *scaled* logits. Dividing by a
temperature of 0.01 multiplies every logit by 100, which is precisely the case
that overflows if you subtracted the max beforehand.
