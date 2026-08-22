import json
from typing import Any, Iterable, Iterator


def parse_sse(chunks: Iterable[str]) -> Iterator[Any]:
    """Parse a server-sent-events byte stream into decoded JSON payloads.

    Args:
        chunks: raw string chunks, split at arbitrary positions.

    Yields:
        The decoded `data` payload of each event, in order.
    """
    raise NotImplementedError
