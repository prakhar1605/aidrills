Under every lexical search engine is one data structure: term to the list of
documents containing it. BM25 scores its postings; filters intersect them; the whole
thing is a dictionary of sets. Interviewers ask for it because the follow-ups —
deletion, phrase queries, sharding — all start here.

Implement `InvertedIndex`.

- `add(doc_id, tokens)` — index a document. Adding the same `doc_id` again
  **replaces** it: none of the old terms may still point at it.
- `remove(doc_id)` — drop a document. Removing one that is not indexed is a no-op,
  not an error.
- `postings(term)` — the doc ids containing `term`, sorted ascending. Unknown terms
  give `[]`.
- `df(term)` — how many documents contain it.
- `search(query_tokens, mode="and")` — `"and"` intersects the postings, `"or"`
  unions them. Results sorted ascending by doc id.
- An empty query returns `[]` in both modes. A term nobody has makes an `"and"`
  query empty but does not affect an `"or"` query.
- Any other `mode` raises `ValueError`.
- `len(index)` is the number of indexed documents.

### What the interviewer is checking

Re-adding a document. The naive index appends postings and never removes them, so
updating a document leaves it matching terms it no longer contains — a bug that
never surfaces in a demo because demos only ever index once. Keeping a forward map
from doc id back to its terms is what makes both `remove` and re-`add` cheap, and
noticing you need it is the point of the question.
