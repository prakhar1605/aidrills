Two lists: `selected` in pick order and `remaining`. Each round scores every
remaining document and moves the winner across. The loop is four lines; the
scoring expression is the problem.
---
The redundancy term is `max(doc_sim[i][j] for j in selected)` — the single most
similar thing you have already picked. Handle the first pick before the loop,
where that `max` has nothing to range over.
---
For "highest score, lowest index on a tie", use
`min(remaining, key=lambda i: (-score(i), i))`. Negating inside a `min` gives you
a total order in one expression, and it does not depend on the iteration order of
`remaining`.
