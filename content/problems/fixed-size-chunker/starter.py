def chunk_text(text: str, size: int, overlap: int = 0) -> list[str]:
    """Split `text` into overlapping fixed-size chunks.

    Args:
        text: the document to split.
        size: maximum characters per chunk.
        overlap: characters each chunk shares with the next.

    Returns:
        Chunks in document order.

    Raises:
        ValueError: if size <= 0, overlap < 0, or overlap >= size.
    """
    raise NotImplementedError
