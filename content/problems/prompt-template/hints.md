Do not reach for `str.format` or a regex `sub` with a callback. Walk the template
one character at a time and append to an output list — the safety property falls
out of never reading that list back.
---
Check for the escaped `{{` *before* you treat `{` as the start of a placeholder,
otherwise `{{name}}` parses as a placeholder named `{name`. Same on the closing
side.
---
Write the walk once as a generator yielding literal chunks and placeholder names,
then build `render` and `variables_used` on top of it. That way a template that
renders is exactly a template whose variables you can enumerate.
