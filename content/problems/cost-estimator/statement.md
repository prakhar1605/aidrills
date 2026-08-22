Somebody has to answer "what did that feature cost us last month", and the answer
comes from usage records and a price sheet. It is arithmetic — which is exactly why
it gets asked: the interviewer wants to see whether you handle a cached-input rate,
an unpriced model, and float rounding without being told to.

Implement `estimate_cost(usages, pricing)`.

Each usage record has a `model`, `input_tokens`, `output_tokens`, and an optional
`cached_input_tokens` (which is **separate** from `input_tokens`, not a subset).
Prices are per **million** tokens.

```python
pricing = {
    "claude-opus-5": {"input": 15.0, "output": 75.0, "cached_input": 1.5},
    "claude-haiku-4-5": {"input": 0.8, "output": 4.0},
}
```

Return a dict:

- `total_usd` — everything, rounded to 6 decimal places.
- `by_model` — one entry per model that appears, each with `calls`, `input_usd`,
  `cached_usd`, `output_usd` and `total_usd`, all rounded the same way.

Rules:

- A model with no `cached_input` price bills cached tokens at its `input` rate.
- A model that is not in `pricing` raises `KeyError` naming the model.
- No usages returns a zero total and an empty `by_model`.
- Missing token counts default to `0`. Negative counts raise `ValueError`.

### What the interviewer is checking

That you round once, at the end of each figure, rather than accumulating rounded
values — the difference shows up as cents that do not reconcile against the
provider's invoice, which is the whole reason anyone builds this. And the cached
rate, because it is the single biggest lever on a real bill and forgetting it makes
your estimate wrong by an order of magnitude on a prompt-cached workload.
