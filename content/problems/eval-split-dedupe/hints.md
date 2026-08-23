Three steps in order: dedupe the whole list, shuffle it, then cut it. Doing the
dedupe after the split is the mistake this problem exists to catch.
---
Use `random.Random(seed)` and shuffle a copy. Seeding the global `random` module
makes the result depend on whatever else in the process touched it.
---
For the counts: floor `n * ratio` for each split, then give the remaining
examples to the splits with the largest fractional parts, ties by index. Assert
to yourself that the three counts sum to `n` — with plain `int()` they usually do
not.
