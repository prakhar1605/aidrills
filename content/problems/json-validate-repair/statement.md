You asked for JSON. You got JSON wrapped in a markdown fence, preceded by
"Sure! Here's the JSON you requested:", with a trailing comma. Structured-output
modes have made this rarer, not gone — every model without one, every fallback
path, and every fine-tune still does it.

Implement `extract_json(text)`. Return the first JSON object or array found in
`text` as a Python value, or `None` if nothing usable is there.

Work in this order:

1. If the text contains a fenced code block, look inside the first one. The fence
   may or may not be tagged `json`.
2. Scan for the first `{` or `[` and take the balanced value that starts there.
   Brackets inside string literals do not count, and neither do escaped quotes.
3. Parse it. If that works, return it — unchanged.
4. Only if it fails, repair and retry. For v1, one repair: drop commas that sit
   immediately before a closing brace or bracket.
5. Still failing, or nothing found, returns `None`.

```python
extract_json('Sure! ```json\n{"ok": true,}\n```')   # {"ok": True}
extract_json('no json here')                        # None
```

### What the interviewer is checking

Step 3 before step 4. Candidates reach for a regex `sub` on the raw text, which
mangles any string value that happens to contain a comma followed by a brace —
the repair corrupts documents that were already valid. Repair is a fallback, never
a preprocessing step. The other thing they look for is the string-aware brace
scanner; counting braces naively breaks on the first payload with a `}` in a
message field.
