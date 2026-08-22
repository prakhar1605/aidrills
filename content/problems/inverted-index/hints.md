One dictionary is not enough. You need `term -> set of doc ids` to answer
queries, and something that answers "which terms did document 7 have?" — without
the second one, updating a document means scanning every posting list.
---
`add` on an existing id should call `remove` first and then insert cleanly. That
keeps the replacement rule in exactly one place instead of duplicated across two
methods.
---
Use sets for the postings: `set.intersection(*sets)` and `set.union(*sets)` are
the two query modes in one line each, and `sorted()` on the way out gives the
stable ordering. Delete a posting set once it empties, or `df()` keeps reporting
terms that no document has any more.
