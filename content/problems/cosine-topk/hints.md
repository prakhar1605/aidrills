Score everything into a list of `(index, similarity)` pairs first, then sort. Do
not try to maintain a top-k heap by hand unless you are asked to — the
interviewer wants the edge cases right before they want it fast.
---
Write the similarity as its own helper taking two vectors. That gives you exactly
one place to put the zero-norm guard, and it will need it for both arguments.
---
Sort with `key=lambda pair: (-pair[1], pair[0])`. And validate every vector's
length before you score any of them, so a malformed corpus raises instead of
half-ranking.
