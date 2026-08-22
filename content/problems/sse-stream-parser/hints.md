Keep one `buffer` string outside the chunk loop. Append each chunk to it, then
drain as many complete events as the buffer currently holds before pulling the
next chunk.
---
`while "\n\n" in buffer:` then `raw, buffer = buffer.split("\n\n", 1)`. That
single line is the whole framing problem — everything left in `buffer` is a
partial event waiting for more bytes.
---
Parse a frame line by line: skip blanks and lines starting with `:`, use
`field, _, value = line.partition(":")`, strip one leading space from `value`,
and collect only the `data` fields. Return a module-level sentinel object for
`[DONE]` so that `None` stays available for "skip this frame".
