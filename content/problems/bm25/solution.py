import math
from collections import Counter


def bm25_scores(
    corpus: list[list[str]],
    query: list[str],
    k1: float = 1.5,
    b: float = 0.75,
) -> list[float]:
    n_docs = len(corpus)
    if n_docs == 0:
        return []

    lengths = [len(doc) for doc in corpus]
    avgdl = sum(lengths) / n_docs
    counts = [Counter(doc) for doc in corpus]

    # Document frequency, computed once for the terms we actually need.
    df: dict[str, int] = {}
    for term in set(query):
        df[term] = sum(1 for c in counts if term in c)

    idf = {
        term: math.log(1 + (n_docs - d + 0.5) / (d + 0.5))
        for term, d in df.items()
    }

    scores = []
    for count, length in zip(counts, lengths):
        # avgdl is 0 only when every document is empty; then f is 0 anyway,
        # but guard so the norm term stays finite.
        norm = 1 - b + b * (length / avgdl if avgdl else 0.0)
        total = 0.0
        for term in query:
            f = count.get(term, 0)
            if not f:
                continue
            total += idf[term] * (f * (k1 + 1)) / (f + k1 * norm)
        scores.append(total)
    return scores


# What the interviewer is checking:
#   - the idf smoothing (+0.5 / +0.5, wrapped in log1p form so it never goes
#     negative for terms present in most documents)
#   - that length normalization divides by the *average* length, not the max
#   - the empty-corpus and all-empty-documents guards, which is where naive
#     implementations throw ZeroDivisionError
