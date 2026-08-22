def chunk_text(text: str, size: int, overlap: int = 0) -> list[str]:
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0:
        raise ValueError("overlap must not be negative")
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    if not text:
        return []

    stride = size - overlap
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size])
        # Stop here rather than after advancing, so the loop never emits a
        # tail chunk that the previous chunk already covers.
        if start + size >= len(text):
            break
        start += stride
    return chunks


# What the interviewer is checking:
#   - the guard on overlap >= size (stride 0 -> infinite loop)
#   - breaking on `start + size >= len(text)` instead of after the increment,
#     which is what produces a duplicated tail chunk
#   - empty input handled without a special case bolted on afterwards
