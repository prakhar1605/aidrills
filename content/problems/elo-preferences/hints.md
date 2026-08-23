Map the winner to A's score once — 1.0, 0.0 or 0.5 — and the two updates become
the same line twice with the arguments swapped.
---
Read both ratings into local variables *before* you write either one back. That
one detail is what this problem is about.
---
`expected_score(a, b) + expected_score(b, a)` is exactly 1, so with the pre-match
snapshot the two updates are equal and opposite: the total rating across all
players never changes. If a test says the total drifted, you updated in place.
