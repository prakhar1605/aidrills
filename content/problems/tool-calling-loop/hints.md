The loop body is always the same four moves: ask, decide, act, record. Write
those four lines first and only then worry about the failure cases.
---
`for _ in range(max_steps)` gives you the budget for free — if the loop finishes
without returning, the budget ran out. That means exactly one `return` inside the
loop (the final answer) and one after it (the budget case).
---
Wrap the tool invocation in `try/except Exception` and turn the exception into
the observation string instead of letting it propagate. Do the unknown-tool check
with `if name not in tools` *before* the try, so a typo'd tool name and a broken
tool produce different, recognizable messages.
