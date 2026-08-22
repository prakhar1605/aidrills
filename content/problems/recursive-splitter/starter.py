def split_text(
    text: str,
    size: int,
    separators: tuple[str, ...] = ("\n\n", "\n", " ", ""),
) -> list[str]:
    """Split `text` into chunks of at most `size`, on the best boundary available.

    Args:
        text: the document.
        size: maximum characters per chunk.
        separators: boundaries to try, best first. "" means a hard slice.

    Returns:
        Chunks in document order; joining them reproduces `text` exactly.

    Raises:
        ValueError: if size <= 0.
    """
    raise NotImplementedError
