Long conversations outgrow the context window. Truncating the front loses the user's
name and the thing they asked for; keeping everything eventually 400s. The standard
answer is to compact: summarize the old turns into one message and keep the recent
ones verbatim.

Implement `WindowMemory`.

`WindowMemory(llm, max_tokens, keep_recent=2)` — use `count_tokens` from `mock_llm`
for every measurement.

- `add(role, content)` appends a message, then compacts if the total exceeds
  `max_tokens`.
- `total_tokens()` — the summary plus every retained message.
- `messages()` — the summary as a leading `system` message when there is one,
  followed by the retained messages.
- `summary` — the current summary, or `None`.

Compaction, once per `add` that overflows:

1. The oldest messages beyond the last `keep_recent` are the ones to fold in. If
   there are none, do nothing — the budget is simply too small and that is not an
   error.
2. Call `llm.complete` **exactly once**, with this prompt:

```text
Summarize the conversation so far, preserving facts, decisions and open questions.

Previous summary:
{the current summary, or "(none)"}

Conversation:
{role}: {content}
{role}: {content}
```

3. Replace the summary with the reply and drop the folded messages.

`keep_recent=0` keeps nothing verbatim. `max_tokens` below 1 raises `ValueError`.

### What the interviewer is checking

That the previous summary goes back into the prompt. Without it, the second
compaction throws away everything from before the first one, and the agent forgets
the user's name at turn 40 — which is the exact bug this design exists to prevent.
Watch out for `keep_recent=0` too: in Python `messages[:-0]` is empty and
`messages[-0:]` is everything, so both slices do the opposite of what you meant.
