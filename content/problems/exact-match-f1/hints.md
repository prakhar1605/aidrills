Write `normalize_answer` first and use it everywhere else. Both metrics are
trivial once the text is normalized, and every subtle bug in this problem lives
in the normalizer.
---
Order matters inside the normalizer: lowercase, then remove punctuation, then
remove articles, then collapse whitespace. Removing articles first leaves
`"the,"` intact because of the comma.
---
For the overlap use `Counter(pred) & Counter(gold)` and sum the values — that is
per-token `min`, which is exactly the multiplicity rule. Return early when the
overlap is zero, before the `2pr / (p + r)` division.
