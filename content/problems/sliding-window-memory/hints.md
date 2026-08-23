Keep the summary and the retained messages as two separate pieces of state.
`messages()` is just the summary turned into a system message, prepended.
---
Compaction splits the list in two: the front folds into the summary, the last
`keep_recent` stay verbatim. Build the transcript from the front half and hand it
to `llm.complete` once.
---
Two traps. Put the existing summary into the prompt — otherwise the second
compaction erases everything before the first. And special-case
`keep_recent == 0`: `messages[:-0]` is `[]` and `messages[-0:]` is the whole
list, so the slices swap meaning exactly when you least want them to.
