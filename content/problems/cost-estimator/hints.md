Two passes. Accumulate raw floats per model in the first, and produce the rounded
report in the second. Mixing them is the bug this problem is looking for.
---
Prices are per million tokens, so every line is `tokens * rate / 1_000_000`.
Cached input is its own line with its own rate, defaulting to the input rate when
the model does not publish one.
---
Sum the *unrounded* subtotals into the grand total, then round it once. Rounding
each model first and adding those gives a total that disagrees with the sum of
the rows by a few cents, which is exactly the complaint that gets filed against
this code.
