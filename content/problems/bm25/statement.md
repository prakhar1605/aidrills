Embeddings lose exact identifiers — error codes, part numbers, function names. Every
serious retrieval stack keeps a lexical scorer alongside the vector index, and that
scorer is BM25. Being able to write it from the formula is table stakes for a
retrieval interview.

Implement `bm25_scores(corpus, query, k1=1.5, b=0.75)`.

`corpus` is a list of documents, each already tokenized into a list of terms.
`query` is a list of terms. Return one score per document, in corpus order.

For a document *d* and query term *q*:

```text
idf(q)   = ln(1 + (N - df(q) + 0.5) / (df(q) + 0.5))
score(q) = idf(q) * (f * (k1 + 1)) / (f + k1 * (1 - b + b * len(d) / avgdl))
```

where `N` is the number of documents, `df(q)` the number of documents containing
*q*, `f` the count of *q* in *d*, and `avgdl` the mean document length.

- A document's score is the sum over the query terms **as given** — a term repeated
  in the query contributes twice.
- A query term that appears in no document contributes `0.0`.
- An empty corpus returns `[]`. An empty query returns `0.0` for every document.
- Empty documents are legal; do not divide by zero.

### What the interviewer is checking

Whether you know what `k1` and `b` actually do. Expect the follow-up: "set `b=0`,
what changed and why?" — the answer is that length normalization is off, so long
documents stop being penalized. And `k1=0` makes term frequency binary: every
match counts once no matter how often it occurs.
