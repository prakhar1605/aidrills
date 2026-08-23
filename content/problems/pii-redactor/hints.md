One compiled pattern per type, plus a fixed list saying what order to apply them
in. The order is part of the answer, not an implementation detail.
---
Use `pattern.sub(callback, text)` rather than a plain string replacement — the
callback is what lets the credit-card rule reject a match it does not like by
returning the original text.
---
Luhn: walk the digits right to left, double every second one, subtract 9 when
doubling pushes it over 9, and check the total is divisible by 10. Strip spaces
and hyphens before you check. And run `phone` last — its pattern happily matches
pieces of everything else.
