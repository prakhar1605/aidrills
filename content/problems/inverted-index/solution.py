class InvertedIndex:
    def __init__(self) -> None:
        self._postings: dict[str, set[int]] = {}
        # The forward map is what makes remove() and re-add() O(terms in doc)
        # instead of a scan over every posting list in the index.
        self._documents: dict[int, set[str]] = {}

    def add(self, doc_id: int, tokens: list[str]) -> None:
        if doc_id in self._documents:
            self.remove(doc_id)

        terms = set(tokens)
        self._documents[doc_id] = terms
        for term in terms:
            self._postings.setdefault(term, set()).add(doc_id)

    def remove(self, doc_id: int) -> None:
        terms = self._documents.pop(doc_id, None)
        if terms is None:
            return
        for term in terms:
            postings = self._postings.get(term)
            if not postings:
                continue
            postings.discard(doc_id)
            if not postings:
                del self._postings[term]  # keep df() honest

    def postings(self, term: str) -> list[int]:
        return sorted(self._postings.get(term, ()))

    def df(self, term: str) -> int:
        return len(self._postings.get(term, ()))

    def search(self, query_tokens: list[str], mode: str = "and") -> list[int]:
        if mode not in ("and", "or"):
            raise ValueError(f'mode must be "and" or "or", got {mode!r}')
        if not query_tokens:
            return []

        sets = [self._postings.get(term, set()) for term in query_tokens]
        if mode == "and":
            matched = set.intersection(*sets) if sets else set()
        else:
            matched = set.union(*sets) if sets else set()
        return sorted(matched)

    def __len__(self) -> int:
        return len(self._documents)


# What the interviewer is checking:
#   - the forward map doc_id -> terms, without which re-adding leaks stale
#     postings
#   - add() delegates to remove() rather than reimplementing the cleanup
#   - empty posting sets are deleted, so df() of a fully removed term is 0 and
#     the index does not grow forever
#   - set.intersection(*sets) short-circuits naturally; an "and" over a missing
#     term is empty because that term's set is empty
