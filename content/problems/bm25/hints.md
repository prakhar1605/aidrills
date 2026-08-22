Compute the three corpus-level quantities before you touch any document:
`N`, the average document length, and the document frequency of each query term.
Doing them inside the per-document loop is the usual reason this comes out
quadratic.
---
Split the score into two halves. The idf half depends only on the term and the
corpus. The saturation half depends on the term count in this document and this
document's length. `Counter(doc)` gives you the counts in one pass.
---
The denominator is `f + k1 * (1 - b + b * len(d) / avgdl)`. Note the
normalization factor multiplies `k1`, it is not added to the whole denominator.
Guard `avgdl == 0` (every document empty) and return `[]` for an empty corpus
before you compute anything.
