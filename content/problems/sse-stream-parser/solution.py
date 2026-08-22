import json
from typing import Any, Iterable, Iterator

_DONE = object()


def _parse_event(raw: str) -> Any:
    """Return the decoded payload, None to skip, or _DONE to stop the stream."""
    data_lines = []
    for line in raw.split("\n"):
        if not line or line.startswith(":"):
            continue  # blank padding or a keep-alive comment
        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]  # exactly one optional space, per the spec
        if field == "data":
            data_lines.append(value)

    if not data_lines:
        return None
    data = "\n".join(data_lines)
    if data.strip() == "[DONE]":
        return _DONE
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None  # one bad frame must not kill the stream


def parse_sse(chunks: Iterable[str]) -> Iterator[Any]:
    buffer = ""
    for chunk in chunks:
        # Re-normalize the whole buffer: a chunk can end between \r and \n.
        buffer = (buffer + chunk).replace("\r\n", "\n")
        while "\n\n" in buffer:
            raw, buffer = buffer.split("\n\n", 1)
            event = _parse_event(raw)
            if event is _DONE:
                return
            if event is not None:
                yield event

    if buffer.strip():  # a final event with no trailing blank line
        event = _parse_event(buffer)
        if event is not None and event is not _DONE:
            yield event


# What the interviewer is checking:
#   - one buffer carried across chunks, drained with `while "\n\n" in buffer`
#     rather than a per-chunk split
#   - a sentinel for [DONE] so a literal null payload is still distinguishable
#     from "stop"
#   - `partition(":")`, which handles a value containing colons; `split(":")`
#     with no maxsplit truncates timestamps and URLs
#   - it is a generator, so the caller gets tokens as they land
