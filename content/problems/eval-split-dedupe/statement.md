The same question appears in your training set and your eval set, punctuated
differently, and your eval score is now measuring memorization. Deduping before
splitting is the difference between a number you can act on and one that only goes
up.

Implement two functions.

`normalize(text)` — lowercase, drop punctuation, collapse whitespace, strip the
ends. This is the dedupe key.

`dedupe_and_split(examples, ratios=(0.8, 0.1, 0.1), seed=0)` — each example is a
dict with a `text` field plus whatever else.

1. Drop examples whose normalized `text` has already been seen. First occurrence
   wins.
2. Shuffle what is left with `random.Random(seed)`, so the same seed always gives
   the same split.
3. Split into train / val / test by the ratios. Use **largest remainder**: floor
   each share, then hand the leftovers to the largest fractional parts, ties going
   to the earlier split. The three counts must sum to the number of deduped
   examples — none may be silently dropped.

Return `{"train": [...], "val": [...], "test": [...], "dropped": n}` holding the
original dicts, with `dropped` counting the duplicates removed.

- Ratios that are not three non-negative numbers summing to `1.0` raise
  `ValueError`.
- An empty input returns three empty splits.

### What the interviewer is checking

That deduping happens **before** the split, not inside each split afterwards — a
per-split dedupe removes duplicates and leaves the cross-split copies exactly where
the leakage is. Then the rounding: `int(n * 0.8)` three times loses examples for most
values of `n`, and losing eval examples silently is the kind of bug that survives for
a year because the number still looks plausible.
