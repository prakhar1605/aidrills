A model asks for four tool calls at once. Two are independent, one needs the first
one's output, one needs everything. Running them serially wastes most of the
latency; running them all at once corrupts the ones with dependencies. What you want
is waves.

Implement `schedule(calls)`.

Each call is `{"id": str, "depends_on": [ids]}` — `depends_on` may be missing.
Return a list of waves. Every id in a wave can run concurrently; a wave may only
start once every earlier wave has finished.

- Each wave is sorted; ids within a wave are unordered so this makes the output
  deterministic.
- A call goes in the **earliest** wave its dependencies allow. Do not pad the
  schedule.
- No calls returns `[]`.
- A duplicate id raises `ValueError`.
- A dependency on an id that does not exist raises `ValueError` naming it.
- A cycle raises `ValueError` naming the ids that are stuck, sorted.
- A call may not depend on itself.

```python
schedule([
    {"id": "a"},
    {"id": "b"},
    {"id": "c", "depends_on": ["a"]},
    {"id": "d", "depends_on": ["b", "c"]},
])
# [["a", "b"], ["c"], ["d"]]
```

### What the interviewer is checking

Whether you produce *levels* rather than a flat topological order. A plain topo sort
answers "is this runnable" but throws away the parallelism, which was the entire
reason for the question. Then the cycle case: a model that references its own output
will produce one, and the schedule has to fail with the offending ids rather than
silently dropping them — an agent that quietly skips a step is worse than one that
errors.
