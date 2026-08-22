Normalize first — lowercase and collapse whitespace — then shingle. Otherwise you
are measuring formatting, and the same paragraph with different line wrapping
looks like a different document.
---
`{s[i:i+n] for i in range(len(s) - n + 1)}` is the shingle set. Guard the case
where the normalized text is shorter than `n`, where that range is empty and you
would return nothing at all.
---
In `dedupe`, keep a parallel list of the shingle sets you have already accepted
and compare each candidate only against those. Compute each candidate's shingles
once, outside the inner loop.
