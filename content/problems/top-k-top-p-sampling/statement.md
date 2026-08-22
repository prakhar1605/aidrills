`temperature`, `top_k` and `top_p` are the three knobs every LLM API exposes, and
candidates who use them daily routinely cannot say what `top_p=0.9` does to the
distribution. This is the sampling step, minus the random draw — deterministic, so
it is actually testable.

Implement `filter_logits(logits, top_k=0, top_p=0.0)`. Return a **new** list the
same length as the input, with rejected positions set to `float("-inf")` and kept
positions unchanged. The caller softmaxes and samples afterwards.

- **top_k**: keep only the `top_k` highest logits. `top_k=0` disables it;
  `top_k >= len(logits)` keeps everything. Ties break toward the lower index.
- **top_p** (nucleus): softmax the logits *that survived top_k*, sort descending,
  and keep the shortest prefix whose cumulative probability reaches `top_p`.
  `top_p=0.0` disables it. Always keep at least one token.
- Apply top_k first, then top_p to what remains.
- Never mutate the input list.

```python
filter_logits([0.0, 0.0, 0.0, 0.0], top_p=0.5)
# probabilities are .25 each; .25 then .50 reaches 0.5 after two tokens
# [0.0, 0.0, -inf, -inf]
```

### What the interviewer is checking

Two things. First, that top-p is computed on probabilities, not on raw logits —
this is the mistake. Second, the "always keep one" guard: with a very peaked
distribution and a small `top_p`, a literal reading of the rule keeps zero tokens
and the sampler divides by zero.
