Do not carry the corpus around as a list of words. Collapse it once into a dict
mapping the symbol tuple to its frequency — every subsequent step reads that dict
and the whole thing stops depending on corpus size.
---
The merge loop is: count pairs across the vocabulary weighted by frequency, pick
the winner, rewrite every entry. Write the rewrite as its own helper taking
`(symbols, pair)` — `encode` needs exactly the same function.
---
For the tie break, find the maximum count first, then `min()` over just the pairs
that reached it. And in `encode`, iterate `merges` in order applying each one
once; a single left-to-right pass suffices, because a merged symbol can never
form a new occurrence of the pair that created it.
