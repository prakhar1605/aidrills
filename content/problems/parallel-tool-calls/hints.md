The output is levels, not a linear order. Each round, take *everything* that is
currently runnable at once — that set is the wave.
---
Keep a `done` set of completed ids and a `pending` map of id to its remaining
dependencies. A call is ready when its dependency set is a subset of `done`.
---
If a round finds nothing ready but `pending` is not empty, everything left is in
or behind a cycle — raise with `sorted(pending)`. Validate duplicates,
self-references and unknown ids before the loop starts, so a bad plan never
produces a partial schedule.
