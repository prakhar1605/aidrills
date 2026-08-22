Keep the patterns in a dict keyed by signal id and just filter it. The whole
function should be three lines once the regexes are written: which fired, sum
their weights, compare to the threshold.
---
Compile every pattern with `re.IGNORECASE | re.MULTILINE`. MULTILINE is what
makes `^\s*(system|assistant)\s*:` match a fake turn marker in the middle of a
document instead of only at the very start.
---
For the two-part signals — a trigger word followed by a target noun — bound the
gap between them: `[^.\n]{0,60}?` instead of `.*`. An unbounded gap will happily
match a "forget" in paragraph one against an "instructions" in paragraph nine.
Sort the signal list before returning it so the output is stable, and give
`sum` a `0.0` start value — the empty sum is otherwise an `int`.
