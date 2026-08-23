Token F1 cannot tell you whether an answer is *good*, so you ask a model. The
scoring is the easy half; the half that decides whether your eval means anything is
what you do when the judge replies with a paragraph instead of a number — silently
dropping those items biases every average you report.

Implement `judge(llm, items, rubric, retries=1)`.

Each item is `{"id", "question", "answer"}`. For each one, call `llm.complete` with
exactly this prompt:

```text
{rubric}

Question: {question}
Answer: {answer}

Reply with "Score: N" where N is 1-5, then a one-line reason.
```

Parse the first `Score: N` in the reply, case-insensitive, anywhere in the text. A
score outside 1–5 does not count as parsed. On a failure to parse, call again — up
to `retries` extra times, so `1 + retries` calls in the worst case.

Return:

```python
{
  "scores": {item_id: int | None},   # None when it never parsed
  "mean": float | None,              # over the parsed scores; None if none parsed
  "distribution": {1: n, 2: n, 3: n, 4: n, 5: n},
  "unparsed": [item_id, ...],        # in item order
  "calls": int,                      # total llm.complete calls
}
```

No items gives a `None` mean, an all-zero distribution and empty everything.

### What the interviewer is checking

That unparsed items are *reported*, not dropped. An eval that quietly averages the
80% of items the judge formatted correctly is measuring the judge's formatting as
much as the model's quality, and nobody looking at the number would know. The
distribution matters for the same reason — a mean of 3.9 made of 4s and a mean of
3.9 made of 1s and 5s are different results, and only one of them is a working
rubric.
