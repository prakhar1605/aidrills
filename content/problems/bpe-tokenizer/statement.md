Byte-pair encoding is why your model spells badly, why numbers tokenize
unpredictably, and why the same prompt costs a different amount in two languages.
It is also about forty lines of code. Interviewers ask for it because most people
who use tokenizers daily have never written the merge loop.

Implement two functions.

`train_bpe(corpus, num_merges)` — `corpus` is a list of words; repeats carry the
frequency. Represent each word as its characters plus the end-of-word marker
`</w>`. Then, `num_merges` times:

1. Count every adjacent symbol pair, weighted by word frequency.
2. Take the most frequent pair. On a tie, take the lexicographically smallest
   pair, so training is deterministic.
3. Merge it everywhere and record it.

Stop early if no pairs remain. Return the merges in the order they were learned,
as a list of `(left, right)` tuples.

`encode(word, merges)` — start from the word's characters plus `</w>`, then apply
each merge in order, scanning left to right and merging non-overlapping
occurrences. Return the resulting symbol list.

- An empty corpus, or `num_merges=0`, returns no merges.
- `encode(word, [])` returns the characters plus `</w>`.
- Joining an encoding and dropping `</w>` must reproduce the original word — for
  any word, including ones never seen in training.

### What the interviewer is checking

That merges are applied *in training order* at encode time, not greedily by length
— get that wrong and the encoder produces tokens the model never saw. Then the tie
break, which is the difference between reproducible training and a tokenizer that
changes when you upgrade Python. And they will ask why `</w>` exists: without it
`est` at the end of `widest` and `est` in the middle of `estimate` collapse into
the same token.
