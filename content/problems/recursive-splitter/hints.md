Three phases, in this order: split on one separator, recurse into anything still
too big, then merge neighbours back together. Trying to do them in one pass is
where this gets hard.
---
`text.split(sep)` throws the separator away. Put it back:
`[part + sep for part in parts[:-1]] + [parts[-1]]`. That single line is what
makes joining the chunks reproduce the input exactly.
---
When you recurse, pass only the separators *after* the one you used — otherwise a
piece that has no paragraph break keeps re-testing for one. And in the merge,
start a new buffer when `len(buffer) + len(piece) > size`, appending whole pieces
only, so nothing can overflow.
