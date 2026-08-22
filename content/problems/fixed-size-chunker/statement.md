Every RAG pipeline starts here. Before anything is embedded, a document has to be
cut into pieces small enough to retrieve and large enough to be useful — and the
pieces have to overlap, or a fact that straddles a boundary becomes unretrievable.

Implement `chunk_text(text, size, overlap)`.

- Return a list of chunks, each at most `size` characters, in document order.
- Consecutive chunks share exactly `overlap` characters: chunk *n* ends with the
  same `overlap` characters that chunk *n+1* begins with.
- The final chunk may be shorter than `size`. Never emit a trailing chunk that is
  already fully contained in the one before it.
- `text=""` returns `[]`.
- Raise `ValueError` when `size <= 0`, when `overlap < 0`, or when
  `overlap >= size` (a stride of zero would loop forever).

```python
chunk_text("abcdefghij", size=4, overlap=1)
# ["abcd", "defg", "ghij"]
```

### What the interviewer is checking

The off-by-one at the boundary, and whether you noticed that `overlap >= size` is
an infinite loop rather than a merely odd input. Character chunking is the warm-up;
the follow-up is always "now make it respect sentence boundaries".
