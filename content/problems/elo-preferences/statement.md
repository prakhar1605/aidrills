Human raters cannot score a model out of ten, but they are good at picking which of
two answers is better. Turning a pile of those pairwise votes into one leaderboard
is what Chatbot Arena does, and the mechanism is chess rating.

Implement two functions.

`expected_score(rating_a, rating_b)` — A's expected result against B:

```text
1 / (1 + 10 ** ((rating_b - rating_a) / 400))
```

`elo_ratings(matches, k=32.0, initial=1000.0)` — every match is
`{"a": name, "b": name, "winner": "a" | "b" | "tie"}`. Process them **in order**,
starting every unseen player at `initial`, and return the final ratings.

The update after a match, where `s` is 1 for a win, 0 for a loss and 0.5 for a tie:

```text
rating_a += k * (s - expected_score(rating_a, rating_b))
rating_b += k * ((1 - s) - expected_score(rating_b, rating_a))
```

- Every player mentioned appears in the result, even if they never won.
- No matches returns an empty dict.
- A `winner` other than `"a"`, `"b"` or `"tie"` raises `ValueError`.
- A player facing themselves raises `ValueError`.
- Use the ratings **as they were before the match** for both updates.

### What the interviewer is checking

That both updates read the pre-match ratings. Updating A and then computing B's
expectation from A's new rating breaks the zero-sum property — total rating stops
being conserved and the leaderboard slowly inflates. Then the intuition:
`k` is how much one vote moves you, and beating a much stronger opponent moves you
further because the expected score was near zero. The follow-up is why order matters
here and what you would do instead — the answer is Bradley-Terry fitted over all the
votes at once.
