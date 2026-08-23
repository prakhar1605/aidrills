Three functions: one that validates, one that resolves an args dict against the
results so far, and the executor. Keeping validation separate is the whole point
of the exercise.
---
Track the ids you have seen *as you validate in order*. A reference is legal only
if its target is already in that set — which rejects both unknown ids and
forward references with one check.
---
Record the attempt number before you make the call, not after, so an exhausted
step still reports how many times it was tried. And return immediately when a
step gives up, so the later steps are absent from `attempts` rather than present
with a zero.
