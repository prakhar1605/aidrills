Token streaming is server-sent events. The SDK hides it until the day you have to
proxy a stream, or the stream stalls, and then you find out that your chunks do not
line up with the protocol's frames at all — one TCP read can end in the middle of a
JSON payload.

Implement `parse_sse(chunks)`, a **generator** that takes an iterable of raw string
chunks and yields one parsed payload per event.

- Events are separated by a blank line. Chunk boundaries are arbitrary and mean
  nothing — a single event may arrive across several chunks, and one chunk may hold
  several events.
- Inside an event, each line is `field: value`. One optional space after the colon
  is part of the syntax and is stripped.
- Only `data` matters. Ignore `event`, `id`, `retry` and anything else.
- Multiple `data` lines in one event are joined with a newline before parsing.
- A line starting with `:` is a keep-alive comment. Ignore it.
- `data: [DONE]` ends the stream. Do not yield it, and ignore anything after it.
- Yield `json.loads` of the data. If one frame's data is not valid JSON, skip that
  frame and keep going.
- Handle `\r\n` as well as `\n`. Flush a final event even if the stream ends
  without a trailing blank line.
- Yield as you go. Never buffer the whole stream.

### What the interviewer is checking

Whether you keep a byte buffer across chunks. Candidates who call `chunk.split` per
chunk write something that works against a local mock and drops tokens against a
real endpoint, because the frame boundary and the chunk boundary are unrelated.
After that: laziness, so a slow consumer applies backpressure instead of collecting
a whole response in memory.
