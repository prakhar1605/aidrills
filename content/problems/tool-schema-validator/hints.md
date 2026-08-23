Collect into a list and sort at the end; never return early. The point of this
function is to tell the model everything that is wrong in one message.
---
Three loops: validate the schema itself, check every required name is present,
then check each supplied argument's type and enum. Keep them separate.
---
The one that decides this problem: `isinstance(True, int)` is `True` in Python.
Reject `bool` explicitly before the `isinstance` check for `integer` and
`number`, or `{"top_k": True}` validates cleanly.
