Everyone writes this, and most people write it as `template.format(**variables)`.
Then a user's message contains a brace and the whole request fails, or worse, it
contains a placeholder name and gets substituted with something they were never
supposed to see.

Implement two functions.

`render(template, variables, strict=True)`

- `{name}` is replaced by `str(variables["name"])`. Whitespace inside the braces is
  ignored, so `{ name }` is the same placeholder.
- `{{` and `}}` are literal braces.
- Substituted values are **inert**. A value containing `{other}` is inserted
  literally and never expanded again.
- A missing variable raises `KeyError` naming it when `strict`, and is left in place
  untouched when not.
- An unmatched `{` or `}`, or an empty placeholder, raises `ValueError`.

`variables_used(template)` — the set of placeholder names, ignoring escaped braces.
Useful for validating a template before anyone runs it.

```python
render("Hi {name}, you said: {msg}", {"name": "Ada", "msg": "use {tools}"})
# "Hi Ada, you said: use {tools}"
```

### What the interviewer is checking

Whether substitution is single-pass. `str.format`, and any implementation that
re-scans its own output, will happily expand a placeholder that arrived inside
user-supplied text — that is template injection, and in a prompt it means an
untrusted string reaching into your system prompt's variables. Writing to an output
buffer you never read back is what makes it safe, and being able to say *why* is the
answer they are listening for.
