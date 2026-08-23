Find all the labels first, in one pass, and record where each one starts. A
field's value is simply the text between its label and the next one — no
per-field regex needed.
---
Anchor the label pattern with `^` and `re.MULTILINE` so a label has to begin a
line. And put `action input` before `action` in the alternation, or the shorter
one matches first and swallows it.
---
Compare the *positions* of the Action and Final Answer labels to decide the kind;
that turns "the model emitted both" from an accident into a rule. Then wrap
`json.loads` in a `try` and fall back to the raw string.
