The model invents an argument, or sends `"5"` where you wanted `5`, and your tool
raises a `TypeError` four frames deep. Validating at the boundary turns that into a
message the model can act on, which is the difference between an agent that
recovers and one that loops.

Implement `validate_args(schema, args)`. Return a **sorted list of error strings**,
empty when the arguments are valid.

The schema is a small subset of JSON Schema:

```python
{
  "properties": {
    "q":    {"type": "string"},
    "top_k": {"type": "integer"},
    "mode": {"type": "string", "enum": ["and", "or"]},
  },
  "required": ["q"],
}
```

Supported types: `string`, `integer`, `number`, `boolean`, `array`, `object`.

Error messages, exactly:

- `missing required property: q`
- `unknown property: colour`
- `q: expected string, got int`
- `mode: expected one of ['and', 'or'], got 'xor'`

Rules:

- Unlisted properties are errors — the model made them up.
- `integer` accepts `int` but not `float`. `number` accepts both.
- **A boolean is never a valid `integer` or `number`**, even though Python says
  `isinstance(True, int)`.
- Only check `enum` after the type is right; do not report both for one property.
- A property whose type name is not supported raises `ValueError` — that is your
  bug, not the model's.
- Missing `properties` or `required` default to empty.

### What the interviewer is checking

`isinstance(True, int) is True`. Python's bool-is-an-int inheritance means the
obvious validator accepts `{"top_k": true}` and passes it straight to a tool that
will do something surprising with it. Beyond that: reporting *all* the errors rather
than the first, because the model needs one message it can fix in a single retry
instead of a slow game of twenty questions.
