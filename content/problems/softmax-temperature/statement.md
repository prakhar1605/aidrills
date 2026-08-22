The warm-up question. It looks like three lines, and the two things it is actually
testing — overflow and the degenerate temperature — are both things people skip.

Implement `softmax(logits, temperature=1.0)`.

- Divide the logits by `temperature`, then exponentiate and normalize. The result
  sums to `1.0`.
- Subtract the maximum before exponentiating. Real logits reach the high hundreds
  and `math.exp(800)` raises `OverflowError`.
- `temperature=0.0` is greedy decoding: return a one-hot vector on the highest
  logit, ties going to the lowest index. Do not divide by zero.
- A negative temperature raises `ValueError`.
- An empty list returns `[]`.

```python
softmax([1.0, 1.0, 1.0])              # [0.333…, 0.333…, 0.333…]
softmax([2.0, 1.0], temperature=0.0)  # [1.0, 0.0]
```

### What the interviewer is checking

That you reach for the max-subtraction without being prompted, and that you noticed
`temperature=0` is a real value a caller passes rather than an error. The follow-up
is the intuition: temperature below 1 sharpens the distribution toward the argmax,
above 1 flattens it toward uniform, and in the limit each end is greedy decoding and
a uniform random draw.
