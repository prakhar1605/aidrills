Nothing needs to run in the background. Store the level and the time you last
looked at it; when someone asks, work out how much has accrued since then.
---
Put that arithmetic in one private helper and call it at the top of both public
methods. Everything else is a comparison.
---
Three clamps decide this problem. Refill is `min(capacity, level + elapsed *
rate)`. Elapsed is `max(0.0, now - last)`, because clocks go backwards. And a
failed `consume` must return before it subtracts anything.
