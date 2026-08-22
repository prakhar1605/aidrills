The follow-up to fixed-size chunking, and the splitter almost every RAG pipeline
actually runs. Cut on paragraph breaks if you can, line breaks if you cannot, spaces
after that, and mid-word only as a last resort — so chunks land on boundaries a
human would have chosen.

Implement `split_text(text, size, separators=("\n\n", "\n", " ", ""))`.

1. Text that already fits returns as a single chunk. Empty text returns `[]`.
2. Otherwise take the **first** separator in the list that occurs in the text. The
   empty separator always "occurs" and means: cut into hard slices of `size`.
3. Split on it, keeping each separator attached to the **end** of the piece before
   it, and drop empty pieces.
4. Any piece still longer than `size` is split again with the *remaining*
   separators.
5. Finally, merge consecutive pieces greedily while the result stays within `size`.

Two invariants the tests lean on:

- `"".join(split_text(text, size)) == text`, always. Nothing is lost or duplicated.
- Every chunk is at most `size` characters.

`size <= 0` raises `ValueError`.

### What the interviewer is checking

The join invariant. Keeping the separator attached is what buys it, and it is the
difference between a splitter you can debug and one that silently eats whitespace —
which then shows up as a chunk that no longer matches the source document when you
try to cite it. After that, the merge step: without it, a document full of short
lines produces hundreds of tiny chunks and your retrieval quality collapses.
