The distance between the start of one chunk and the start of the next is not
`size` — it is `size - overlap`. Give that quantity a name before you write the
loop.
---
Walk a `start` index forward by `stride = size - overlap`, slicing
`text[start:start + size]` each time. Python slicing clamps past the end, so the
short final chunk needs no special handling.
---
The redundant-tail bug comes from where you break. Append the chunk, then break
immediately if `start + size >= len(text)` — checking *before* you advance
`start`. And validate `overlap < size` up front: a stride of zero never
terminates.
