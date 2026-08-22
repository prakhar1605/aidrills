Before you can improve a RAG system you have to score it, and before you can score
it you have to stop counting `"The Eiffel Tower."` as wrong when the gold answer is
`"eiffel tower"`. This is the SQuAD scorer — the metric under most extractive QA
evals, and the one people copy without reading.

Implement three functions.

`normalize_answer(text)` — lowercase, strip punctuation, drop the articles `a`,
`an`, `the`, and collapse runs of whitespace to single spaces. Strip the ends.

`exact_match(pred, golds)` — `1.0` if the normalized prediction equals any
normalized gold, else `0.0`.

`f1_score(pred, golds)` — token-level F1 against the best-matching gold. Split
normalized text on whitespace. Overlap counts **multiplicity**: if the prediction
says `cat` twice and the gold once, that is one match, not two.

```text
precision = overlap / len(pred_tokens)
recall    = overlap / len(gold_tokens)
f1        = 2 * precision * recall / (precision + recall)
```

- Empty prediction and empty gold score `1.0`. One empty and the other not scores
  `0.0`. No overlap scores `0.0`.
- `golds` is a list — return the maximum over it.

### What the interviewer is checking

The multiplicity rule (a `set` intersection is the common wrong answer), and the
degenerate cases, which is where a scorer silently reports `nan` and poisons a
whole eval run. The real discussion afterwards is why token F1 is a bad metric for
anything generative — which is how you get to LLM-as-judge.
