Before function calling was an API feature, agents ran on a text protocol: the model
writes `Thought:`, `Action:`, `Action Input:`, and you parse it back out. Plenty of
systems still do — open models, fine-tunes, anything behind a completion endpoint —
and the parser is where they break, because the model does not read your format
spec as carefully as you wrote it.

Implement `parse_react(text)`.

Recognized labels, at the start of a line and case-insensitive: `Thought:`,
`Action:`, `Action Input:`, `Final Answer:`. Each field runs until the next
recognized label or the end of the text.

Return either

```python
{"kind": "action", "thought": str | None, "action": str, "input": object}
{"kind": "final",  "thought": str | None, "answer": str}
```

- Whichever of `Action` or `Final Answer` appears **first** decides the kind. Models
  produce both.
- `Action Input` is JSON when it parses as JSON, and the raw stripped string
  otherwise. A missing `Action Input` on an action is an empty dict.
- `action` is the first line of the Action field, stripped — models append
  commentary.
- `Final Answer` keeps its newlines, stripped at the ends.
- A missing `Thought` gives `None`.
- Text with neither an `Action` nor a `Final Answer` raises `ValueError`.

### What the interviewer is checking

That a malformed generation raises something a caller can handle rather than
returning a half-built dict, and that "the model emitted both an action and a final
answer" has a defined winner instead of whichever branch your `if` happened to check
first. The JSON-or-string fallback is the other half: models write
`Action Input: weather in Paris` about as often as they write valid JSON, and an
agent that crashes on that is an agent that crashes.
