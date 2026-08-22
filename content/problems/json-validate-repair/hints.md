Three separate jobs: find the candidate substring, parse it, repair only if the
parse failed. Write them as three steps and the ordering bug never happens.
---
The scanner needs four pieces of state: where the value started, the nesting
depth, whether you are inside a string, and whether the previous character was a
backslash. Once you are inside a string, nothing else matters until it closes.
---
Try `json.loads(candidate)` first and return immediately on success. Only in the
`except json.JSONDecodeError` branch apply `re.sub(r",(\s*[}\]])", r"\1", ...)`
and try once more. Return `None` if that fails too — never raise.
