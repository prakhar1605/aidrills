Score each item independently, collecting into a dict keyed by item id. Compute
the mean, the distribution and the unparsed list at the end, from that dict —
not incrementally.
---
`re.search(r"score\s*:\s*(\d+)", reply, re.IGNORECASE)` handles the formatting
variation. Then check the range separately: a number outside 1-5 is a parse
failure, not a score.
---
Loop `1 + retries` times per item and break on the first success, counting every
call. Seed the distribution with all five buckets at zero before you count, so
callers never have to check whether a key exists.
