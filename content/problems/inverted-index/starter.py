class InvertedIndex:
    """Term -> the documents containing it."""

    def __init__(self) -> None:
        raise NotImplementedError

    def add(self, doc_id: int, tokens: list[str]) -> None:
        """Index a document, replacing any earlier version of it."""
        raise NotImplementedError

    def remove(self, doc_id: int) -> None:
        """Drop a document. A no-op if it was never indexed."""
        raise NotImplementedError

    def postings(self, term: str) -> list[int]:
        """Doc ids containing `term`, ascending."""
        raise NotImplementedError

    def df(self, term: str) -> int:
        """Document frequency of `term`."""
        raise NotImplementedError

    def search(self, query_tokens: list[str], mode: str = "and") -> list[int]:
        """Boolean search over the postings.

        Raises:
            ValueError: if mode is not "and" or "or".
        """
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
